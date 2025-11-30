"""
Comprehensive Evaluation Runner
Executes all evaluation tests and generates detailed report
"""
import sys
import os
import argparse
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.evaluation.metrics_collector import MetricsCollector
from tests.fixtures.test_scenarios import ALL_SCENARIOS, print_dataset_summary


def run_comprehensive_evaluation(
    scenarios=None,
    output_dir="evaluation_results",
    verbose=True
):
    """
    Run comprehensive evaluation across all test scenarios
    
    Args:
        scenarios: List of TestScenario objects (default: ALL_SCENARIOS)
        output_dir: Directory to save results
        verbose: Print progress
    
    Returns:
        dict: Evaluation results and metrics
    """
    scenarios = scenarios or ALL_SCENARIOS
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("="*70)
    print("🚀 STARTING COMPREHENSIVE MEDICAL AI EVALUATION")
    print("="*70)
    print(f"Test Scenarios: {len(scenarios)}")
    print(f"Output Directory: {output_dir}")
    print(f"Timestamp: {timestamp}")
    print("="*70)
    
    # Initialize system
    if verbose:
        print("\n📦 Initializing Medical Diagnostic Graph...")
    
    medical_graph = MedicalDiagnosticGraph()
    metrics_collector = MetricsCollector()
    
    # Track results
    results = {
        "metadata": {
            "timestamp": timestamp,
            "total_scenarios": len(scenarios),
            "model": "gemini-2.5-flash-lite"
        },
        "scenario_results": [],
        "failures": [],
        "performance_summary": {}
    }
    
    # Execute each scenario
    for i, scenario in enumerate(scenarios, 1):
        if verbose:
            print(f"\n[{i}/{len(scenarios)}] Testing: {scenario.name} ({scenario.id})")
        
        try:
            # Start metrics collection
            metrics_collector.start_execution(scenario.id, scenario.input_text)
            
            # Execute graph
            result = medical_graph.analyze(
                user_input=scenario.input_text,
                image=scenario.image,
                chat_history=scenario.chat_history
            )
            
            # End metrics collection
            execution_metrics = metrics_collector.end_execution(
                success=result.get("success", False),
                final_state=result
            )
            
            # Validate against expectations
            validation = {
                "scenario_id": scenario.id,
                "success": result.get("success", False),
                "latency": execution_metrics.total_latency_seconds,
                "latency_within_limit": execution_metrics.total_latency_seconds <= scenario.max_latency_seconds,
                "agents_executed": execution_metrics.agents_executed,
                "plan_length": execution_metrics.plan_length,
                "revision_count": execution_metrics.revision_count
            }
            
            # Check expected agents
            if scenario.expected_agents:
                expected_set = set(scenario.expected_agents)
                actual_set = set(execution_metrics.agents_executed)
                validation["agents_match"] = expected_set == actual_set
                validation["missing_agents"] = list(expected_set - actual_set)
                validation["unexpected_agents"] = list(actual_set - expected_set)
            
            # Check severity
            if scenario.expected_severity and execution_metrics.severity_level:
                validation["severity_match"] = execution_metrics.severity_level == scenario.expected_severity
                validation["expected_severity"] = scenario.expected_severity
                validation["actual_severity"] = execution_metrics.severity_level
            
            results["scenario_results"].append(validation)
            
            if verbose:
                status = "✅" if validation["success"] else "❌"
                print(f"   {status} Success: {validation['success']}")
                print(f"   ⏱️  Latency: {validation['latency']:.2f}s")
                print(f"   🤖 Agents: {', '.join(execution_metrics.agents_executed)}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results["failures"].append({
                "scenario_id": scenario.id,
                "scenario_name": scenario.name,
                "error": str(e)
            })
    
    # Aggregate metrics
    if verbose:
        print("\n" + "="*70)
        print("📊 AGGREGATING METRICS...")
        print("="*70)
    
    aggregated_metrics = metrics_collector.aggregate_metrics()
    agentic_scores = aggregated_metrics.calculate_scores()
    
    # Save detailed results
    detailed_results = {
        **results,
        "aggregated_metrics": aggregated_metrics.to_dict(),
        "agentic_scores": agentic_scores,
        "executions": [e.to_dict() for e in metrics_collector.executions]
    }
    
    results_file = os.path.join(output_dir, f"evaluation_results_{timestamp}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Print summary
    metrics_collector.print_summary()
    
    # Generate summary report
    generate_summary_report(detailed_results, output_dir, timestamp)
    
    return detailed_results


def generate_summary_report(results, output_dir, timestamp):
    """Generate human-readable summary report"""
    
    report_file = os.path.join(output_dir, f"evaluation_report_{timestamp}.md")
    
    aggregated = results["aggregated_metrics"]
    scores = results["agentic_scores"]
    scenario_results = results["scenario_results"]
    failures = results["failures"]
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Medical Diagnostic Multi-Agent System - Evaluation Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Model:** {results['metadata']['model']}\n\n")
        
        f.write("## Executive Summary\n\n")
        
        success_rate = (aggregated['successful_executions'] / aggregated['total_executions']) * 100
        f.write(f"- **Total Test Scenarios:** {aggregated['total_executions']}\n")
        f.write(f"- **Success Rate:** {success_rate:.1f}%\n")
        f.write(f"- **Average Latency:** {aggregated['avg_latency_seconds']:.2f}s\n")
        f.write(f"- **Overall Agentic Score:** {scores['overall']:.1f}/10\n\n")
        
        f.write("## Agentic Capability Scores (0-10 scale)\n\n")
        f.write("| Dimension | Score | Grade |\n")
        f.write("|-----------|-------|-------|\n")
        
        score_grades = [
            ("Autonomy", scores.get('autonomy', 0)),
            ("Reactivity", scores.get('reactivity', 0)),
            ("Proactivity", scores.get('proactivity', 0)),
            ("Coordination", scores.get('coordination', 0)),
            ("Goal Orientation", scores.get('goal_orientation', 0)),
            ("Adaptability", scores.get('adaptability', 0)),
            ("Memory/Context", scores.get('memory', 0)),
            ("Tool Use", scores.get('tool_use', 0)),
            ("Constraint Adherence", scores.get('constraint_adherence', 0)),
            ("Error Recovery", scores.get('error_recovery', 0)),
        ]
        
        for dimension, score in score_grades:
            grade = "A+" if score >= 9.5 else "A" if score >= 8.5 else "B+" if score >= 7.5 else "B" if score >= 6.5 else "C" if score >= 5.5 else "D"
            f.write(f"| {dimension} | {score:.1f} | {grade} |\n")
        
        f.write(f"| **Overall** | **{scores['overall']:.1f}** | **{grade}** |\n\n")
        
        f.write("## Performance Metrics\n\n")
        f.write(f"- **Average Plan Length:** {aggregated['avg_plan_length']:.1f} steps\n")
        f.write(f"- **Average Revisions:** {aggregated['avg_revisions']:.1f}\n")
        f.write(f"- **Min Latency:** {aggregated['min_latency_seconds']:.2f}s\n")
        f.write(f"- **Max Latency:** {aggregated['max_latency_seconds']:.2f}s\n")
        f.write(f"- **Agents per Execution:** {aggregated['avg_agents_per_execution']:.1f}\n\n")
        
        f.write("## Agent Usage Statistics\n\n")
        agent_usage = aggregated['agent_usage_count']
        f.write("| Agent | Usage Count | Success Rate |\n")
        f.write("|-------|-------------|-------------|\n")
        for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True):
            success_rate = aggregated['agent_success_rate'].get(agent, 0) * 100
            f.write(f"| {agent} | {count} | {success_rate:.0f}% |\n")
        
        f.write("\n## Quality Metrics\n\n")
        f.write(f"- **Average Confidence:** {aggregated['avg_confidence']:.2f}\n")
        f.write(f"- **Emergency Detection Rate:** {aggregated['emergency_detection_rate']*100:.1f}%\n")
        f.write(f"- **Language Adherence:** {aggregated['language_adherence_rate']*100:.1f}%\n")
        f.write(f"- **Constraint Violations:** {aggregated['constraint_violations']}\n\n")
        
        f.write("## Error Analysis\n\n")
        f.write(f"- **Total Errors:** {aggregated['error_count']}\n")
        f.write(f"- **Recovery Success Rate:** {aggregated['recovery_success_rate']*100:.1f}%\n\n")
        
        if failures:
            f.write("### Failed Scenarios\n\n")
            for failure in failures:
                f.write(f"- **{failure['scenario_name']}** ({failure['scenario_id']}): {failure['error']}\n")
        
        f.write("\n## Scenario-Level Results\n\n")
        
        # Group by category
        by_category = {}
        for result in scenario_results:
            scenario_id = result['scenario_id']
            # Find scenario to get category
            for scenario in results['metadata'].get('scenarios', []):
                if scenario.get('id') == scenario_id:
                    category = scenario.get('category', 'unknown')
                    break
            else:
                category = 'unknown'
            
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        for category, category_results in by_category.items():
            f.write(f"### {category.replace('_', ' ').title()}\n\n")
            success_count = sum(1 for r in category_results if r['success'])
            f.write(f"**Success Rate:** {success_count}/{len(category_results)}\n\n")
        
        f.write("## Recommendations\n\n")
        
        # Generate recommendations based on scores
        if scores.get('proactivity', 0) < 7:
            f.write("- ⚠️ **Proactivity:** Consider implementing predictive planning and anticipatory actions\n")
        
        if scores.get('memory', 0) < 7:
            f.write("- ⚠️ **Memory/Context:** Implement long-term memory and conversation history persistence\n")
        
        if scores.get('error_recovery', 0) < 7:
            f.write("- ⚠️ **Error Recovery:** Add retry logic, fallback models, and circuit breakers\n")
        
        if aggregated['avg_latency_seconds'] > 10:
            f.write("- ⚠️ **Performance:** Consider caching, parallelization, or faster models\n")
        
        if aggregated['language_adherence_rate'] < 0.9:
            f.write("- ⚠️ **Constraints:** Strengthen language constraint enforcement in prompts\n")
        
        f.write("\n## Conclusion\n\n")
        
        if scores['overall'] >= 8:
            f.write("The system demonstrates **strong agentic capabilities** across most dimensions. ")
        elif scores['overall'] >= 6:
            f.write("The system shows **good agentic capabilities** with room for improvement. ")
        else:
            f.write("The system has **moderate agentic capabilities** and requires significant enhancement. ")
        
        f.write(f"Overall score of **{scores['overall']:.1f}/10** indicates a ")
        
        if scores['overall'] >= 8:
            f.write("production-ready system with minor optimizations needed.\n")
        elif scores['overall'] >= 6:
            f.write("functional system that would benefit from targeted improvements.\n")
        else:
            f.write("system in early stages requiring substantial development.\n")
    
    print(f"📄 Summary report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive evaluation of medical AI system")
    parser.add_argument("--output-dir", default="evaluation_results", help="Output directory for results")
    parser.add_argument("--category", help="Run only scenarios from specific category")
    parser.add_argument("--scenario-id", help="Run only specific scenario by ID")
    parser.add_argument("--quiet", action="store_true", help="Minimize output")
    
    args = parser.parse_args()
    
    # Filter scenarios if requested
    scenarios = ALL_SCENARIOS
    if args.category:
        from tests.fixtures.test_scenarios import get_scenarios_by_category
        scenarios = get_scenarios_by_category(args.category)
        print(f"Running {len(scenarios)} scenarios from category: {args.category}")
    
    if args.scenario_id:
        from tests.fixtures.test_scenarios import get_scenario_by_id
        scenario = get_scenario_by_id(args.scenario_id)
        if scenario:
            scenarios = [scenario]
            print(f"Running single scenario: {scenario.name}")
        else:
            print(f"Scenario not found: {args.scenario_id}")
            return
    
    # Run evaluation
    results = run_comprehensive_evaluation(
        scenarios=scenarios,
        output_dir=args.output_dir,
        verbose=not args.quiet
    )
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()
