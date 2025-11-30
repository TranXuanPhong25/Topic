"""
Tests for Constraint Adherence
Evaluates language, style, and urgency constraint following
"""
import pytest
from src.evaluation.evaluators import ConstraintEvaluator
from tests.fixtures.test_scenarios import VIETNAMESE_SCENARIOS


@pytest.mark.constraints
@pytest.mark.parametrize("scenario", VIETNAMESE_SCENARIOS, ids=lambda s: s.id)
def test_vietnamese_language_adherence(medical_graph, metrics_collector, scenario):
    """Test system responds in Vietnamese when requested"""
    
    metrics_collector.start_execution(scenario.id, scenario.input_text)
    
    result = medical_graph.analyze(
        user_input=scenario.input_text,
        chat_history=scenario.chat_history
    )
    
    execution_metrics = metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    assert result.get("success"), "Vietnamese case execution failed"
    
    final_response = result.get("final_response", "")
    assert final_response, "No final response provided"
    
    # Detect language
    detected_language = ConstraintEvaluator.detect_language(final_response)
    
    # Record constraint check
    metrics_collector.record_constraint_check(
        expected_language=scenario.expected_language,
        actual_language=detected_language
    )
    
    assert detected_language == "Vietnamese", \
        f"Expected Vietnamese response, got {detected_language}. Response: {final_response[:200]}"


@pytest.mark.constraints
def test_english_language_default(medical_graph, metrics_collector):
    """Test system uses English by default"""
    
    test_input = "I have a fever"
    
    metrics_collector.start_execution("english_default", test_input)
    
    result = medical_graph.analyze(user_input=test_input)
    
    metrics_collector.end_execution(
        success=result.get("success", False),
        final_state=result
    )
    
    final_response = result.get("final_response", "")
    detected_language = ConstraintEvaluator.detect_language(final_response)
    
    metrics_collector.record_constraint_check(
        expected_language="English",
        actual_language=detected_language
    )
    
    assert detected_language == "English", \
        f"Expected English response, got {detected_language}"


@pytest.mark.constraints
def test_style_constraint_brief(medical_graph):
    """Test system provides brief responses when requested"""
    
    # Explicitly request brief response (would need to be passed via context)
    test_input = "Quick question: what causes fever?"
    
    result = medical_graph.analyze(user_input=test_input)
    
    final_response = result.get("final_response", "")
    word_count = len(final_response.split())
    
    # Brief responses should be under 150 words for simple questions
    # This is a soft constraint based on the question type
    assert word_count < 300, \
        f"Response too long for simple question: {word_count} words"


@pytest.mark.constraints
def test_style_constraint_detailed(medical_graph):
    """Test system provides detailed responses when appropriate"""
    
    # Complex query that warrants detailed response
    test_input = "I need detailed information about my symptoms: persistent cough, fever, fatigue for 2 weeks. What could this be and what should I do?"
    
    result = medical_graph.analyze(user_input=test_input)
    
    final_response = result.get("final_response", "")
    word_count = len(final_response.split())
    
    # Detailed responses should be thorough (>100 words)
    assert word_count > 100, \
        f"Response too brief for detailed request: {word_count} words"


@pytest.mark.constraints
def test_urgency_emergency_handling(medical_graph):
    """Test emergency urgency is properly reflected in response"""
    
    test_input = "Severe chest pain and difficulty breathing"
    
    result = medical_graph.analyze(user_input=test_input)
    
    final_response = result.get("final_response", "").lower()
    
    # Should include urgent action words
    urgent_phrases = [
        "call 911",
        "emergency",
        "immediately",
        "urgent",
        "seek immediate",
        "cấp cứu",
        "khẩn cấp",
        "ngay lập tức"
    ]
    
    has_urgent_language = any(phrase in final_response for phrase in urgent_phrases)
    
    assert has_urgent_language, \
        f"Emergency case missing urgent action language. Response: {final_response[:200]}"


@pytest.mark.constraints
def test_constraint_propagation_through_plan(medical_graph):
    """Test constraints are propagated through plan steps"""
    
    test_input = "Tôi bị sốt"  # "I have fever" in Vietnamese
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Execution failed"
    
    plan = result.get("plan", [])
    
    # Check that plan steps include context with language constraint
    for step in plan:
        context = step.get("context", "")
        if context:
            # If context is provided, it should mention language
            # (Note: May need adjustment based on actual implementation)
            if "Language:" in context or "language:" in context.lower():
                assert "Vietnamese" in context or "vietnamese" in context.lower(), \
                    f"Vietnamese constraint not propagated to {step.get('step')}"


@pytest.mark.constraints
def test_mixed_language_handling(medical_graph):
    """Test system handles mixed language input appropriately"""
    
    # Mixed English and Vietnamese
    test_input = "I have sốt và đau đầu"
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Mixed language execution failed"
    
    final_response = result.get("final_response", "")
    
    # Should detect predominant language or default to one
    # Just verify we get a response
    assert len(final_response) > 50, "Response too short for mixed language input"


@pytest.mark.constraints
def test_constraint_consistency_across_agents(medical_graph):
    """Test constraints are consistently followed by all agents"""
    
    test_input = "Tôi nên làm gì để điều trị?"
    chat_history = [
        {"role": "user", "content": "Tôi bị cảm"},
        {"role": "assistant", "content": "Bạn có triệu chứng gì?"}
    ]
    
    result = medical_graph.analyze(
        user_input=test_input,
        chat_history=chat_history
    )
    
    final_response = result.get("final_response", "")
    
    # All parts of the response should be in Vietnamese
    detected_language = ConstraintEvaluator.detect_language(final_response)
    
    assert detected_language == "Vietnamese", \
        "Language constraint not maintained throughout multi-agent execution"


@pytest.mark.constraints
def test_tone_appropriateness(medical_graph):
    """Test response tone is appropriate for medical context"""
    
    test_cases = [
        ("I'm worried about chest pain", ["professional", "reassuring", "clear"]),
        ("What are your hours?", ["friendly", "helpful", "brief"]),
        ("EMERGENCY: Can't breathe!", ["urgent", "direct", "immediate action"]),
    ]
    
    for test_input, expected_tone_attributes in test_cases:
        result = medical_graph.analyze(user_input=test_input)
        
        final_response = result.get("final_response", "").lower()
        
        # Verify professional medical tone (no slang, appropriate language)
        inappropriate_terms = ["lol", "omg", "dude", "bro", "sick" ]  # casual terms
        
        has_inappropriate = any(term in final_response for term in inappropriate_terms)
        
        assert not has_inappropriate, \
            f"Inappropriate tone for medical context in: {test_input}"
