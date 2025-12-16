import asyncio
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_core.messages import HumanMessage, AIMessage
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.evaluation.evaluator import ComprehensiveEvaluator
from src.evaluation.metrics import QUALITATIVE_CRITERIA, LATENCY_THRESHOLDS, PASS_FAIL_CRITERIA

# ============================================================================
# MAIN EVALUATION LOOP
# ============================================================================

async def run_comprehensive_evaluation(dataset_path: str, output_path: str, delay: int = 5):
    # If dataset_path is relative, try to find it relative to this file
    if not os.path.isabs(dataset_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(current_dir, dataset_path)
        if os.path.exists(potential_path):
            dataset_path = potential_path
            
    print(f"Loading dataset from {dataset_path}...")
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {dataset_path}")
        return

    print("Initializing Medical Diagnostic System...")
    try:
        graph = MedicalDiagnosticGraph()
        evaluator = ComprehensiveEvaluator()
    except Exception as e:
        print(f"Error initializing: {e}")
        return

    results = []
    print(f"Starting comprehensive evaluation of {len(test_cases)} cases...\n")

    for i, case in enumerate(test_cases):
        case_id = case.get('id', 'unknown')
        case_type = case.get('type', 'standard')
        raw_inputs = case.get('input', '')
        
        # Normalize input to list for multi-turn support
        inputs = raw_inputs if isinstance(raw_inputs, list) else [raw_inputs]
        
        print(f"--- Case {case_id} ({case_type}): {case.get('description', '')} ---")
        
        chat_history = []
        case_results = []
        
        # Execute each turn
        for turn_idx, user_input in enumerate(inputs):
            print(f"  > Turn {turn_idx + 1}: {user_input[:50]}...")
            
            # Fault Injection Check
            if not user_input:
                print("  >> Running Fault Injection: Empty Input")
                
            start_time = time.time()
            final_response_text = ""
            full_result = {}
            error_occured = False
            
            try:
                full_result = await graph.analyze(user_input=user_input, chat_history=chat_history)
                final_response_text = full_result.get('final_response', '')
            except Exception as e:
                error_occured = True
                final_response_text = f"SYSTEM_ERROR: {str(e)}"
                print(f"  !! System Error: {e}")
                
            tct = time.time() - start_time
            
            # Latency warning
            latency_status = "⚡ EXCELLENT"
            if tct > LATENCY_THRESHOLDS["warning"]:
                latency_status = "❌ FAIL"
            elif tct > LATENCY_THRESHOLDS["acceptable"]:
                latency_status = "⚠️  WARNING"
            elif tct > LATENCY_THRESHOLDS["good"]:
                latency_status = "✓ ACCEPTABLE"
            elif tct > LATENCY_THRESHOLDS["excellent"]:
                latency_status = "✓ GOOD"
            
            print(f"  Response: {final_response_text[:100]}... (TCT: {tct:.2f}s {latency_status})")
            
            # Update history for next turn
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=final_response_text))
            
            # --- Evaluation (Per Turn) ---
            # 1. Formal
            formal_score = evaluator.verify_formal_constraints(full_result if not error_occured else {})
            
            # 2. Content matches (Only check on final turn?) 
            # Strategy: If it's the LAST turn, we do strict checking against 'expected_diagnosis'.
            # Intermediate turns might just need to proceed.
            is_last_turn = (turn_idx == len(inputs) - 1)
            
            accuracy = 0.0
            fidelity = 0.0
            
            if is_last_turn:
                expected_diagnoses = [d.lower() for d in case.get('expected_diagnosis', [])]
                required_phrases = [p.lower() for p in case.get('required_phrases', [])]
                final_lower = final_response_text.lower()
                
                # Accuracy
                if not expected_diagnoses:
                     accuracy = 0.0 if error_occured else 1.0
                else:
                    for diagnosis in expected_diagnoses:
                        if diagnosis in final_lower:
                            accuracy = 1.0
                            break
                            
                # Fidelity
                if required_phrases:
                    found = sum(1 for p in required_phrases if p in final_lower)
                    fidelity = found / len(required_phrases)
                else:
                    fidelity = 1.0
            else:
                # Intermediate turns: Assume 1.0 if no error
                accuracy = 1.0 if not error_occured else 0.0
                fidelity = 1.0 # Skip fidelity for intermediate
            
            # 3. Qualitative
            qual_scores = {}
            if not error_occured and final_response_text:
                context = f"Case Type: {case_type}. Turn {turn_idx+1}/{len(inputs)}."
                if is_last_turn: 
                    context += f" Expected Behavior: {case.get('expected_behavior')}"
                
                # Simple throttling/retry handling handled inside evaluator, but lets be safe
                try:
                    qual_scores = await evaluator.grade_qualitative_metrics(
                        user_input, 
                        final_response_text, 
                        context
                    )
                except Exception as e:
                    print(f"  Evaluator Failed: {e}")
            
            # Store turn result
            case_results.append({
                "turn": turn_idx,
                "input": user_input,
                "response": final_response_text,
                "tct": tct,
                "accuracy": accuracy,
                "fidelity": fidelity,
                "formal": formal_score,
                "qualitative": qual_scores
            })

        # Aggregate Result for Case (Average of turns or just use last?)
        # Let's use Last Turn for hard metrics, Average for TCT
        last_turn = case_results[-1]
        avg_tct = sum(r['tct'] for r in case_results) / len(case_results)
        
        results.append({
            "id": case_id,
            "type": case_type,
            "input": inputs, # Store full list
            "last_response": last_turn['response'],
            "tct": avg_tct, # Avg TCT per turn
            "total_time": sum(r['tct'] for r in case_results),
            "max_tct": max(r['tct'] for r in case_results),
            "formal_verification": last_turn['formal'],
            "accuracy": last_turn['accuracy'],
            "rule_fidelity": last_turn['fidelity'],
            "qualitative": last_turn['qualitative'] # Use last turn's qual score
        })
        print(f"  -> Case {case_id} Completed. Acc: {last_turn['accuracy']:.2f}, Fid: {last_turn['fidelity']:.2f}, TCT(avg): {avg_tct:.2f}s\n")
        
        if i < len(test_cases) - 1:
            await asyncio.sleep(delay)

    # ========================================================================
    # GENERATE REPORT
    # ========================================================================
    
    if not results:
        return

    # Calculate overall metrics
    avg_tct = sum(r['tct'] for r in results) / len(results)
    avg_acc = sum(r['accuracy'] for r in results) / len(results)
    avg_fid = sum(r['rule_fidelity'] for r in results) / len(results)
    
    # Calculate latency percentiles
    all_tcts = sorted([r['tct'] for r in results])
    p50_tct = all_tcts[len(all_tcts) // 2]
    p95_tct = all_tcts[int(len(all_tcts) * 0.95)] if len(all_tcts) > 20 else all_tcts[-1]
    p99_tct = all_tcts[int(len(all_tcts) * 0.99)] if len(all_tcts) > 50 else all_tcts[-1]
    max_tct = max(all_tcts)
    
    # Qual averages
    qual_avgs = {k: 0.0 for k in QUALITATIVE_CRITERIA}
    valid_qual_count = 0
    
    for r in results:
        q = r.get('qualitative', {})
        if q:
            valid_qual_count += 1
            for k in QUALITATIVE_CRITERIA:
                qual_avgs[k] += q.get(k, 0.0)
            
    if valid_qual_count > 0:
        for k in qual_avgs:
            qual_avgs[k] /= valid_qual_count
    
    avg_qual = sum(qual_avgs.values()) / len(qual_avgs) if qual_avgs else 0.0
    
    # Categorize results
    by_category = {}
    for r in results:
        cat = r['type']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)
    
    # Pass/Fail checks
    passes = []
    fails = []
    
    if avg_acc >= PASS_FAIL_CRITERIA['min_accuracy']:
        passes.append(f"✓ Accuracy ({avg_acc:.1%})")
    else:
        fails.append(f"✗ Accuracy ({avg_acc:.1%} < {PASS_FAIL_CRITERIA['min_accuracy']:.1%})")
    
    if avg_fid >= PASS_FAIL_CRITERIA['min_rule_fidelity']:
        passes.append(f"✓ Rule Fidelity ({avg_fid:.1%})")
    else:
        fails.append(f"✗ Rule Fidelity ({avg_fid:.1%} < {PASS_FAIL_CRITERIA['min_rule_fidelity']:.1%})")
    
    if avg_qual >= PASS_FAIL_CRITERIA['min_qualitative']:
        passes.append(f"✓ Qualitative ({avg_qual:.1%})")
    else:
        fails.append(f"✗ Qualitative ({avg_qual:.1%} < {PASS_FAIL_CRITERIA['min_qualitative']:.1%})")
    
    if avg_tct <= PASS_FAIL_CRITERIA['max_avg_latency']:
        passes.append(f"✓ Avg Latency ({avg_tct:.2f}s)")
    else:
        fails.append(f"✗ Avg Latency ({avg_tct:.2f}s > {PASS_FAIL_CRITERIA['max_avg_latency']:.1f}s)")
    
    if p95_tct <= PASS_FAIL_CRITERIA['max_p95_latency']:
        passes.append(f"✓ P95 Latency ({p95_tct:.2f}s)")
    else:
        fails.append(f"✗ P95 Latency ({p95_tct:.2f}s > {PASS_FAIL_CRITERIA['max_p95_latency']:.1f}s)")
    
    overall_pass = len(fails) == 0

    report = f"""# Comprehensive System Evaluation Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Cases**: {len(results)}  
**Overall Status**: {'✅ PASS' if overall_pass else '❌ FAIL'}  

---

## 🎯 Pass/Fail Summary

### Passed Criteria
{chr(10).join('- ' + p for p in passes) if passes else '- None'}

### Failed Criteria
{chr(10).join('- ' + f for f in fails) if fails else '- None'}

---

## 📊 Executive Summary

### Core Metrics
| Metric | Value | Status |
|--------|-------|--------|
| **Accuracy** | {avg_acc:.1%} | {'✓' if avg_acc >= PASS_FAIL_CRITERIA['min_accuracy'] else '✗'} |
| **Rule Fidelity** | {avg_fid:.1%} | {'✓' if avg_fid >= PASS_FAIL_CRITERIA['min_rule_fidelity'] else '✗'} |
| **Avg Qualitative** | {avg_qual:.1%} | {'✓' if avg_qual >= PASS_FAIL_CRITERIA['min_qualitative'] else '✗'} |

### Performance Statistics (Latency)
| Metric | Value | Status |
|--------|-------|--------|
| **Avg TCT** | {avg_tct:.2f}s | {'✓' if avg_tct <= PASS_FAIL_CRITERIA['max_avg_latency'] else '✗'} |
| **P50 (Median)** | {p50_tct:.2f}s | - |
| **P95** | {p95_tct:.2f}s | {'✓' if p95_tct <= PASS_FAIL_CRITERIA['max_p95_latency'] else '✗'} |
| **P99** | {p99_tct:.2f}s | - |
| **Max** | {max_tct:.2f}s | - |

---

## 📈 Qualitative Metrics (Gemini 1.5 Flash)

| Metric | Score |
|--------|-------|
"""
    for k, v in qual_avgs.items():
        report += f"| {k} | {v:.2f} |\n"
    
    report += f"\n**Average**: {avg_qual:.2f}\n\n---\n\n"
    
    # Category breakdown
    report += "## 📁 Results by Category\n\n"
    for cat, cat_results in sorted(by_category.items()):
        cat_acc = sum(r['accuracy'] for r in cat_results) / len(cat_results)
        cat_fid = sum(r['rule_fidelity'] for r in cat_results) / len(cat_results)
        cat_tct = sum(r['tct'] for r in cat_results) / len(cat_results)
        report += f"### {cat.upper()} ({len(cat_results)} cases)\n"
        report += f"- Accuracy: {cat_acc:.1%}\n"
        report += f"- Rule Fidelity: {cat_fid:.1%}\n"
        report += f"- Avg TCT: {cat_tct:.2f}s\n\n"

    report += "---\n\n## 📝 Detailed Case Logs\n\n"
    for r in results:
        inputs_str = str(r['input'])
        if len(inputs_str) > 80: inputs_str = inputs_str[:80] + "..."
        snippet = r['last_response'].replace('\n', ' ')[:100]
        
        # Latency status
        tct_status = "⚡"
        if r['tct'] > LATENCY_THRESHOLDS['warning']:
            tct_status = "❌"
        elif r['tct'] > LATENCY_THRESHOLDS['acceptable']:
            tct_status = "⚠️"
        elif r['tct'] > LATENCY_THRESHOLDS['good']:
            tct_status = "✓"
        
        report += f"### {r['id']} ({r['type']})\n"
        report += f"- **Accuracy**: {r['accuracy']:.2f} | **Fidelity**: {r['rule_fidelity']:.2f} | **TCT**: {r['tct']:.2f}s {tct_status}\n"
        report += f"- **Input**: {inputs_str}\n"
        report += f"- **Response**: {snippet}{'...' if len(r['last_response']) > 100 else ''}\n\n"

    print("Generating report...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="test_dataset.json")
    parser.add_argument("--output", default="evaluation_report.md")
    parser.add_argument("--delay", type=int, default=3)
    args = parser.parse_args()
    
    asyncio.run(run_comprehensive_evaluation(args.dataset, args.output, args.delay))
