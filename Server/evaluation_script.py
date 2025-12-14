import asyncio
import json
import time
import os
import sys
from datetime import datetime

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph

def calculate_metrics(results):
    total_cases = len(results)
    if total_cases == 0:
        return 0, 0, 0

    total_accuracy = 0
    total_rule_fidelity = 0
    total_tct = 0

    for res in results:
        total_accuracy += res['accuracy_score']
        total_rule_fidelity += res['rule_fidelity_score']
        total_tct += res['tct']

    avg_accuracy = total_accuracy / total_cases
    avg_rule_fidelity = total_rule_fidelity / total_cases
    avg_tct = total_tct / total_cases

    return avg_accuracy, avg_rule_fidelity, avg_tct

async def run_evaluation(dataset_path: str, output_path: str, delay: int = 15):
    print(f"Loading dataset from {dataset_path}...")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    print("Initializing Medical Diagnostic System...")
    try:
        graph = MedicalDiagnosticGraph()
    except Exception as e:
        print(f"Error initializing graph: {e}")
        print("Please make sure you have the GOOGLE_API_KEY set in your .env file.")
        return

    results = []

    print(f"Starting evaluation of {len(test_cases)} cases...\n")


    for i, case in enumerate(test_cases):
        case_id = case.get('id', 'unknown')
        user_input = case.get('input', '')
        expected_diagnoses = [d.lower() for d in case.get('expected_diagnosis', [])]
        required_phrases = [p.lower() for p in case.get('required_phrases', [])]
        
        print(f"--- Case {case_id}: {case.get('description', '')} ---")
        print(f"Input: {user_input}")

        # Measure Task Completion Time (TCT)
        start_time = time.time()
        try:
            response_data = await graph.analyze(user_input=user_input)
            final_response = response_data.get('final_response', '')
        except Exception as e:
            print(f"Error processing case {case_id}: {e}")
            final_response = ""
        end_time = time.time()
        
        tct = end_time - start_time
        print(f"Response: {final_response[:100]}...")
        print(f"TCT: {tct:.4f}s")

        # Calculate Accuracy (Keyword match)
        final_response_lower = final_response.lower()
        accuracy_score = 0
        if not expected_diagnoses:
            # If no diagnosis expected (e.g. greeting), consider accurate if response is not empty
            accuracy_score = 1.0 if final_response else 0.0
        else:
            for diagnosis in expected_diagnoses:
                if diagnosis in final_response_lower:
                    accuracy_score = 1.0
                    break
        
        print(f"Accuracy: {accuracy_score}")

        # Calculate Rule Fidelity
        rule_fidelity_score = 0
        if not required_phrases:
            rule_fidelity_score = 1.0 # No rules to break
        else:
            found_phrases = 0
            for phrase in required_phrases:
                if phrase in final_response_lower:
                    found_phrases += 1
            rule_fidelity_score = found_phrases / len(required_phrases) if required_phrases else 1.0
        
        print(f"Rule Fidelity: {rule_fidelity_score}")

        results.append({
            "id": case_id,
            "input": user_input,
            "response": final_response,
            "tct": tct,
            "accuracy_score": accuracy_score,
            "rule_fidelity_score": rule_fidelity_score
        })
        print("\n")
        
        # Delay to avoid rate limits
        if i < len(test_cases) - 1:
            print(f"Sleeping for {delay} seconds to respect API rate limits...")
            await asyncio.sleep(delay)

    avg_acc, avg_rf, avg_tct = calculate_metrics(results)

    report = f"""# System Evaluation Report
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Cases: {len(results)}

## Quantitative Metrics
- **Average Accuracy**: {avg_acc:.2%}
- **Average Rule Fidelity**: {avg_rf:.2%}
- **Average Task Completion Time (TCT)**: {avg_tct:.4f} seconds

## Detailed Results
| ID | Input | Accuracy | Rule Fidelity | TCT (s) |
|----|-------|----------|---------------|---------|
"""
    for res in results:
        report += f"| {res['id']} | {res['input'][:30]}... | {res['accuracy_score']} | {res['rule_fidelity_score']:.2f} | {res['tct']:.4f} |\n"

    print(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Medical Diagnostic System")
    parser.add_argument("--dataset", default="test_dataset.json", help="Path to test dataset JSON")
    parser.add_argument("--output", default="evaluation_report.md", help="Path to output report MD")
    parser.add_argument("--delay", type=int, default=15, help="Delay in seconds between test cases (to avoid rate limits)")
    
    args = parser.parse_args()
    
    asyncio.run(run_evaluation(args.dataset, args.output, args.delay))
