"""
Quick Start Guide for Evaluation Pipeline
Run this to see test dataset and basic evaluation setup
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.fixtures.test_scenarios import print_dataset_summary, ALL_SCENARIOS


def main():
    print("\n" + "="*70)
    print("🎯 MEDICAL AI EVALUATION PIPELINE - QUICK START")
    print("="*70)
    
    # Show dataset
    print_dataset_summary()
    
    # Show example scenarios
    print("\n📋 EXAMPLE SCENARIOS:\n")
    
    for scenario in ALL_SCENARIOS[:3]:
        print(f"• {scenario.name} ({scenario.category})")
        print(f"  Input: {scenario.input_text}")
        print(f"  Expected: {scenario.expected_agents}")
        print()
    
    # Show how to run tests
    print("="*70)
    print("🚀 HOW TO RUN EVALUATION:")
    print("="*70)
    print()
    print("1. Run all tests with pytest:")
    print("   pytest tests/evaluation/")
    print()
    print("2. Run specific test category:")
    print("   pytest tests/evaluation/ -m agentic")
    print("   pytest tests/evaluation/ -m diagnosis")
    print("   pytest tests/evaluation/ -m constraints")
    print()
    print("3. Run comprehensive evaluation:")
    print("   python tests/evaluation/run_evaluation.py")
    print()
    print("4. Run specific category:")
    print("   python tests/evaluation/run_evaluation.py --category emergency")
    print()
    print("5. Run single scenario:")
    print("   python tests/evaluation/run_evaluation.py --scenario-id simple_001")
    print()
    print("="*70)
    print("📊 AVAILABLE TEST MARKERS:")
    print("="*70)
    print()
    print("  - agentic: Tests for agentic capabilities")
    print("  - diagnosis: Tests for diagnosis quality")
    print("  - constraints: Tests for constraint adherence")
    print("  - performance: Tests for performance metrics")
    print("  - integration: End-to-end integration tests")
    print("  - slow: Tests that take >5 seconds")
    print()
    print("="*70)
    print("📁 EVALUATION OUTPUTS:")
    print("="*70)
    print()
    print("  Results saved to: evaluation_results/")
    print("    - evaluation_results_YYYYMMDD_HHMMSS.json (detailed)")
    print("    - evaluation_report_YYYYMMDD_HHMMSS.md (summary)")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
