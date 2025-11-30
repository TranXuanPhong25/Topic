"""
Tests for Supervisor Agent Routing Decisions
Evaluates autonomy, decision-making, and planning capabilities
"""
import pytest
from tests.fixtures.test_scenarios import (
    SIMPLE_DIAGNOSIS_SCENARIOS,
    EMERGENCY_SCENARIOS,
    FAQ_SCENARIOS,
    APPOINTMENT_SCENARIOS
)


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", SIMPLE_DIAGNOSIS_SCENARIOS, ids=lambda s: s.id)
def test_supervisor_routes_simple_diagnosis(medical_graph, metrics_collector, scenario):
    """Test supervisor correctly routes simple diagnosis cases"""
    
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
    
    # Assertions
    assert result.get("success"), f"Execution failed: {result.get('error')}"
    
    # Check plan structure
    plan = result.get("plan", [])
    assert len(plan) > 0, "No plan was created"
    
    if scenario.expected_plan_length:
        assert len(plan) == scenario.expected_plan_length, \
            f"Expected {scenario.expected_plan_length} steps, got {len(plan)}"
    
    # Check expected agents were executed
    if scenario.expected_agents:
        executed_agents = [step["step"] for step in plan if step.get("status") == "completed"]
        for expected_agent in scenario.expected_agents:
            assert expected_agent in executed_agents, \
                f"Expected agent '{expected_agent}' not executed. Got: {executed_agents}"
    
    # Check latency
    assert execution_metrics.total_latency_seconds <= scenario.max_latency_seconds, \
        f"Latency {execution_metrics.total_latency_seconds:.2f}s exceeds limit {scenario.max_latency_seconds}s"


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", EMERGENCY_SCENARIOS, ids=lambda s: s.id)
def test_supervisor_handles_emergencies(medical_graph, metrics_collector, scenario):
    """Test supervisor correctly identifies and prioritizes emergency cases"""
    
    metrics_collector.start_execution(scenario.id, scenario.input_text)
    
    result = medical_graph.analyze(
        user_input=scenario.input_text,
        chat_history=scenario.chat_history
    )
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "Emergency case execution failed"
    
    # Check severity detection
    diagnosis = result.get("diagnosis", {})
    risk_assessment = diagnosis.get("risk_assessment", {})
    severity = risk_assessment.get("severity")
    
    assert severity == scenario.expected_severity, \
        f"Expected severity {scenario.expected_severity}, got {severity}"
    
    # Check red flags
    if scenario.expected_red_flags:
        red_flags = risk_assessment.get("red_flags", [])
        assert len(red_flags) > 0, "No red flags detected for emergency case"
        
        # At least one expected red flag should be present
        red_flags_text = " ".join(red_flags).lower()
        found_flag = any(
            expected.lower() in red_flags_text 
            for expected in scenario.expected_red_flags
        )
        assert found_flag, f"Expected red flags not found. Got: {red_flags}"
    
    # Emergency cases should be fast
    assert execution_metrics.total_latency_seconds <= scenario.max_latency_seconds, \
        f"Emergency response too slow: {execution_metrics.total_latency_seconds:.2f}s"


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", FAQ_SCENARIOS, ids=lambda s: s.id)
def test_supervisor_routes_to_conversation_agent(medical_graph, metrics_collector, scenario):
    """Test supervisor correctly routes FAQ queries to conversation agent"""
    
    metrics_collector.start_execution(scenario.id, scenario.input_text)
    
    result = medical_graph.analyze(user_input=scenario.input_text)
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "FAQ execution failed"
    
    # Check conversation_agent was used
    plan = result.get("plan", [])
    executed_agents = [step["step"] for step in plan if step.get("status") == "completed"]
    
    assert "conversation_agent" in executed_agents, \
        f"conversation_agent not used for FAQ. Got: {executed_agents}"
    
    # FAQ should be fast
    assert execution_metrics.total_latency_seconds <= scenario.max_latency_seconds


@pytest.mark.agentic
@pytest.mark.parametrize("scenario", APPOINTMENT_SCENARIOS, ids=lambda s: s.id)
def test_supervisor_routes_to_appointment_scheduler(medical_graph, metrics_collector, scenario):
    """Test supervisor correctly routes appointment requests"""
    
    metrics_collector.start_execution(scenario.id, scenario.input_text)
    
    result = medical_graph.analyze(user_input=scenario.input_text)
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "Appointment scheduling failed"
    
    # Check appointment_scheduler was used
    plan = result.get("plan", [])
    executed_agents = [step["step"] for step in plan if step.get("status") == "completed"]
    
    assert "appointment_scheduler" in executed_agents, \
        f"appointment_scheduler not used. Got: {executed_agents}"


@pytest.mark.agentic
def test_supervisor_creates_complete_plan(medical_graph, metrics_collector):
    """Test supervisor creates well-formed plans with goals and context"""
    
    test_input = "I have fever and cough for 3 days"
    metrics_collector.start_execution("plan_structure_test", test_input)
    
    result = medical_graph.analyze(user_input=test_input)
    
    metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "Execution failed"
    
    plan = result.get("plan", [])
    assert len(plan) > 0, "No plan created"
    
    # Check plan structure
    for step in plan:
        assert "step" in step, "Plan step missing 'step' field"
        assert "description" in step, "Plan step missing 'description' field"
        assert "goal" in step, "Plan step missing 'goal' field"
        assert "status" in step, "Plan step missing 'status' field"
        
        # Goals should be meaningful
        goal = step.get("goal", "")
        assert len(goal) > 10, f"Goal too short: {goal}"
        
        # Status should be valid
        status = step.get("status")
        assert status in ["pending", "current", "completed", "skipped"], \
            f"Invalid status: {status}"


@pytest.mark.agentic
def test_supervisor_adapts_plan_on_new_request(medical_graph, metrics_collector):
    """Test supervisor extends plan when user makes new request after diagnosis"""
    
    # First diagnosis
    initial_input = "I have fever"
    metrics_collector.start_execution("plan_adaptation_test", initial_input)
    
    result1 = medical_graph.analyze(user_input=initial_input)
    
    assert result1.get("success"), "Initial diagnosis failed"
    
    # Now user asks for treatment advice
    follow_up = "What should I do to treat this?"
    chat_history = [
        {"role": "user", "content": initial_input},
        {"role": "assistant", "content": result1.get("final_response", "")}
    ]
    
    result2 = medical_graph.analyze(
        user_input=follow_up,
        chat_history=chat_history
    )
    
    execution_metrics = metrics_collector.end_execution(
        success=result2.get("success", False),
        final_state=result2
    )
    
    assert result2.get("success"), "Follow-up request failed"
    
    # Check that recommender was added to plan
    plan = result2.get("plan", [])
    executed_agents = [step["step"] for step in plan]
    
    # Should include recommender for treatment advice
    # (Note: This test assumes supervisor extends plan, may need adjustment based on actual behavior)
    assert len(plan) > 2, "Plan not extended for treatment request"


@pytest.mark.agentic
@pytest.mark.slow
def test_supervisor_avoids_unnecessary_replanning(medical_graph, metrics_collector):
    """Test supervisor doesn't replan when work is already complete"""
    
    test_input = "I have a headache"
    metrics_collector.start_execution("no_replan_test", test_input)
    
    result = medical_graph.analyze(user_input=test_input)
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "Execution failed"
    
    # Check plan changes
    plan_changes = execution_metrics.plan_changes
    
    # For simple diagnosis, plan should be stable (0-1 changes)
    assert plan_changes <= 1, f"Too many plan changes: {plan_changes}"


@pytest.mark.agentic
def test_supervisor_decision_reasoning(medical_graph):
    """Test supervisor provides reasoning for routing decisions"""
    
    test_input = "Severe chest pain and difficulty breathing"
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Execution failed"
    
    # Check that plan steps have reasoning through descriptions
    plan = result.get("plan", [])
    for step in plan:
        description = step.get("description", "")
        assert len(description) > 5, f"Step {step.get('step')} has insufficient description"
