"""
Pytest Configuration and Fixtures
Shared test fixtures for medical diagnostic system evaluation
"""
import pytest
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.evaluation.metrics_collector import MetricsCollector


@pytest.fixture(scope="session")
def medical_graph():
    """Initialize medical diagnostic graph once per test session"""
    return MedicalDiagnosticGraph()


@pytest.fixture(scope="function")
def metrics_collector():
    """Create fresh metrics collector for each test"""
    return MetricsCollector()


@pytest.fixture
def sample_simple_symptoms():
    """Simple symptom input for basic diagnosis tests"""
    return {
        "input": "I have fever and headache for 2 days",
        "expected_agents": ["symptom_extractor", "diagnosis_engine"],
        "expected_plan_length": 2,
        "max_latency_seconds": 10.0,
        "expected_severity": "LOW"
    }


@pytest.fixture
def sample_emergency_symptoms():
    """Emergency symptom input for critical path tests"""
    return {
        "input": "Severe chest pain radiating to left arm, difficulty breathing, cold sweats",
        "expected_agents": ["symptom_extractor", "diagnosis_engine"],
        "expected_severity": "EMERGENCY",
        "expected_red_flags": ["chest pain", "breathing difficulty"],
        "max_latency_seconds": 5.0
    }


@pytest.fixture
def sample_vietnamese_input():
    """Vietnamese language input for constraint adherence tests"""
    return {
        "input": "Tôi bị sốt và đau đầu 2 ngày rồi",
        "expected_language": "Vietnamese",
        "expected_agents": ["symptom_extractor", "diagnosis_engine"],
        "constraint": {
            "language": "Vietnamese",
            "style": "Brief"
        }
    }


@pytest.fixture
def sample_mixed_intent():
    """Mixed intent input for filtering tests"""
    return {
        "input": "Hello! I have fever and cough. Also, what are your clinic hours?",
        "expected_agents": ["symptom_extractor", "diagnosis_engine"],
        "filtered_symptoms": "fever and cough",
        "should_filter_greeting": True
    }


@pytest.fixture
def sample_image_analysis():
    """Image analysis test case (placeholder)"""
    return {
        "input": "Check this rash on my arm",
        "image": "base64_placeholder",  # TODO: Add real test image
        "expected_agents": ["image_analyzer", "diagnosis_engine"],
        "expected_plan_length": 2
    }


@pytest.fixture
def sample_multi_turn_conversation():
    """Multi-turn conversation for context tracking tests"""
    return {
        "turns": [
            {"input": "I have a headache", "expected_agent": "symptom_extractor"},
            {"input": "Since yesterday morning", "expected_agent": "symptom_extractor"},
            {"input": "Now it's worse and I have nausea", "expected_agent": "symptom_extractor"}
        ],
        "expected_final_agents": ["symptom_extractor", "diagnosis_engine"],
        "should_combine_history": True
    }


@pytest.fixture
def test_execution_context():
    """Context for tracking test execution metadata"""
    return {
        "test_run_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "environment": "test",
        "model": "gemini-2.5-flash-lite"
    }


@pytest.fixture
def langsmith_config():
    """LangSmith tracing configuration for tests"""
    return {
        "project": os.getenv("LANGSMITH_PROJECT", "medical-diagnosis-eval"),
        "tracing_enabled": os.getenv("LANGSMITH_TRACING", "true").lower() == "true",
        "tags": ["test", "evaluation"]
    }


# Pytest markers for categorizing tests
def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "agentic: tests for agentic capabilities (autonomy, coordination, etc.)"
    )
    config.addinivalue_line(
        "markers", "performance: tests for latency, token efficiency, etc."
    )
    config.addinivalue_line(
        "markers", "diagnosis: tests for diagnosis accuracy and quality"
    )
    config.addinivalue_line(
        "markers", "constraints: tests for language/style/urgency constraint adherence"
    )
    config.addinivalue_line(
        "markers", "error_recovery: tests for error handling and fallback behavior"
    )
    config.addinivalue_line(
        "markers", "integration: end-to-end integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: tests that take longer than 5 seconds"
    )


# Hooks for test reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for metrics"""
    outcome = yield
    rep = outcome.get_result()
    
    # Store test result in item for later access
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionfinish(session, exitstatus):
    """Hook to generate evaluation report after all tests"""
    if hasattr(session.config, 'workerinput'):
        # Skip on worker nodes in parallel execution
        return
    
    print("\n" + "="*70)
    print("📊 EVALUATION SUMMARY")
    print("="*70)
    
    # Collect test statistics
    passed = len([i for i in session.items if hasattr(i, 'rep_call') and i.rep_call.passed])
    failed = len([i for i in session.items if hasattr(i, 'rep_call') and i.rep_call.failed])
    skipped = len([i for i in session.items if hasattr(i, 'rep_call') and i.rep_call.skipped])
    total = len(session.items)
    
    print(f"✅ Passed:  {passed}/{total}")
    print(f"❌ Failed:  {failed}/{total}")
    print(f"⏭️  Skipped: {skipped}/{total}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    print("="*70)
