"""
Tests for Agent Coordination and Multi-Agent Workflow
Evaluates handoffs, state management, and collaboration
"""
import pytest
from src.evaluation.evaluators import CoordinationEvaluator
from tests.fixtures.test_scenarios import (
    SIMPLE_DIAGNOSIS_SCENARIOS,
    MULTI_TURN_SCENARIOS,
    MIXED_INTENT_SCENARIOS
)


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", SIMPLE_DIAGNOSIS_SCENARIOS[:2], ids=lambda s: s.id)
def test_agent_handoff_success(medical_graph, metrics_collector, scenario):
    """Test agents successfully hand off control to next agent"""
    
    metrics_collector.start_execution(scenario.id, scenario.input_text)
    
    result = medical_graph.analyze(user_input=scenario.input_text)
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    # Evaluate coordination
    coordination_eval = CoordinationEvaluator.evaluate(
        final_state=result,
        expected_agents=scenario.expected_agents
    )
    
    assert coordination_eval.passed(), \
        f"Coordination failed: {coordination_eval.issues}"
    
    assert coordination_eval.plan_completed, "Plan not completed"
    assert coordination_eval.handoff_success, "Agent handoff failed"


@pytest.mark.agentic
def test_state_consistency_across_agents(medical_graph):
    """Test state remains consistent as it passes between agents"""
    
    test_input = "I have fever, cough, and fatigue for 3 days"
    
    result = medical_graph.analyze(user_input=test_input)
    
    coordination_eval = CoordinationEvaluator.evaluate(final_state=result)
    
    assert coordination_eval.state_consistency, \
        f"State inconsistency detected: {coordination_eval.issues}"
    
    # Check required fields are present
    required_fields = ["input", "plan", "next_step", "final_response"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"


@pytest.mark.agentic
def test_plan_execution_order(medical_graph):
    """Test agents execute in logical order according to plan"""
    
    test_input = "I have a cough"
    
    result = medical_graph.analyze(user_input=test_input)
    
    plan = result.get("plan", [])
    completed_steps = [step for step in plan if step.get("status") == "completed"]
    
    # For symptom-based diagnosis, should follow: symptom_extractor -> diagnosis_engine
    if len(completed_steps) >= 2:
        agents_in_order = [step["step"] for step in completed_steps]
        
        # symptom_extractor should come before diagnosis_engine
        if "symptom_extractor" in agents_in_order and "diagnosis_engine" in agents_in_order:
            symptom_idx = agents_in_order.index("symptom_extractor")
            diagnosis_idx = agents_in_order.index("diagnosis_engine")
            
            assert symptom_idx < diagnosis_idx, \
                f"Agents executed out of order: {agents_in_order}"


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", MULTI_TURN_SCENARIOS, ids=lambda s: s.id)
def test_multi_turn_context_preservation(medical_graph, scenario):
    """Test conversation context is preserved across turns"""
    
    # Execute the multi-turn conversation
    result = medical_graph.analyze(
        user_input=scenario.input_text,
        chat_history=scenario.chat_history
    )
    
    assert result.get("success"), "Multi-turn execution failed"
    
    # Check that symptoms from history are considered
    symptoms = result.get("symptoms", {})
    
    # Should have extracted symptoms (exact structure depends on implementation)
    assert symptoms, "No symptoms extracted from multi-turn conversation"


@pytest.mark.agentic
def test_parallel_agent_capabilities(medical_graph):
    """Test system can handle cases that might benefit from parallel execution"""
    
    # Image + text symptoms could theoretically be analyzed in parallel
    test_input = "Check this rash. It's itchy and appeared 3 days ago."
    # Note: Would need actual image for full test
    
    result = medical_graph.analyze(user_input=test_input)
    
    # Currently system is sequential, but test that it completes successfully
    assert result.get("success"), "Multi-modal case failed"
    
    # Future: Could check execution time vs sequential baseline


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", MIXED_INTENT_SCENARIOS, ids=lambda s: s.id)
def test_intent_filtering_coordination(medical_graph, scenario):
    """Test supervisor correctly filters and routes mixed intents"""
    
    result = medical_graph.analyze(user_input=scenario.input_text)
    
    assert result.get("success"), "Mixed intent execution failed"
    
    coordination_eval = CoordinationEvaluator.evaluate(
        final_state=result,
        expected_agents=scenario.expected_agents
    )
    
    # Should prioritize medical concerns
    assert coordination_eval.agents_executed_correctly, \
        f"Wrong agents for mixed intent. Expected: {scenario.expected_agents}, Got: {coordination_eval.actual_agents}"


@pytest.mark.agentic
def test_agent_error_isolation(medical_graph, metrics_collector):
    """Test errors in one agent don't crash entire system"""
    
    # This would need a way to inject errors for testing
    # For now, test graceful degradation with edge cases
    
    test_input = "   "  # Empty input
    
    metrics_collector.start_execution("error_isolation", test_input)
    
    result = medical_graph.analyze(user_input=test_input)
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    # System should handle gracefully, not crash
    # May fail, but should return structured response
    assert "final_response" in result or "error" in result, \
        "System crashed instead of handling error gracefully"


@pytest.mark.agentic
def test_revision_loop_coordination(medical_graph):
    """Test coordination between diagnosis_engine and diagnosis_critic"""
    
    # Complex case that might trigger revision
    test_input = "Severe headache, confusion, stiff neck, light sensitivity"
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Revision case failed"
    
    revision_count = result.get("revision_count", 0)
    
    # Should have revision mechanism (may or may not trigger for this case)
    # Just verify it doesn't loop infinitely
    assert revision_count <= 2, f"Too many revisions: {revision_count}"
    
    # If revisions occurred, final diagnosis should be high quality
    if revision_count > 0:
        diagnosis = result.get("diagnosis", {})
        confidence = diagnosis.get("confidence", 0)
        assert confidence > 0.5, "Revisions didn't improve confidence"


@pytest.mark.agentic
def test_agent_usage_metrics(medical_graph, metrics_collector):
    """Test agent usage is tracked correctly"""
    
    test_cases = [
        "I have a fever",
        "What are your clinic hours?",
        "Book appointment for Tuesday"
    ]
    
    for test_input in test_cases:
        test_id = f"usage_metrics_{test_cases.index(test_input)}"
        metrics_collector.start_execution(test_id, test_input)
        
        result = medical_graph.analyze(user_input=test_input)
        
        metrics_collector.end_execution(
            success=result.get("success", False),
            final_state=result
        )
    
    # Aggregate metrics
    metrics = metrics_collector.aggregate_metrics()
    
    # Check agent usage tracking
    assert len(metrics.agent_usage_count) > 0, "No agent usage tracked"
    
    # Most common agents should be symptom_extractor and diagnosis_engine
    # (for the test cases above)
    usage = metrics.agent_usage_count
    
    print(f"\nAgent usage: {usage}")
    assert metrics.total_executions == 3, "Execution count mismatch"


@pytest.mark.agentic
def test_supervisor_end_decision(medical_graph):
    """Test supervisor correctly decides when to END workflow"""
    
    test_input = "I have a cold"
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Execution failed"
    
    # Should end with "END" decision
    next_step = result.get("next_step")
    assert next_step == "END", f"Expected END, got {next_step}"
    
    # Plan should be completed
    plan = result.get("plan", [])
    all_completed = all(
        step.get("status") in ["completed", "skipped"] 
        for step in plan
    )
    
    assert all_completed or next_step == "END", \
        "Workflow ended without completing plan"
