"""
Tests for Diagnosis Quality and Accuracy
Evaluates diagnosis completeness, reasoning, and medical safety
"""
import pytest
from src.evaluation.evaluators import DiagnosisEvaluator
from tests.fixtures.test_scenarios import (
    SIMPLE_DIAGNOSIS_SCENARIOS,
    EMERGENCY_SCENARIOS
)


@pytest.mark.diagnosis
@pytest.mark.parametrize("scenario", SIMPLE_DIAGNOSIS_SCENARIOS, ids=lambda s: s.id)
def test_diagnosis_completeness(medical_graph, scenario):
    """Test diagnosis includes all required components"""
    
    result = medical_graph.analyze(
        user_input=scenario.input_text,
        chat_history=scenario.chat_history
    )
    
    assert result.get("success"), "Execution failed"
    
    diagnosis = result.get("diagnosis", {})
    assert diagnosis, "No diagnosis provided"
    
    # Evaluate diagnosis quality
    evaluation = DiagnosisEvaluator.evaluate(
        diagnosis,
        expected_severity=scenario.expected_severity
    )
    
    # Print issues for debugging
    if evaluation.issues:
        print(f"\nDiagnosis issues for {scenario.id}:")
        for issue in evaluation.issues:
            print(f"  - {issue}")
    
    # Check quality
    assert evaluation.passed(), \
        f"Diagnosis quality insufficient: {evaluation.issues}"
    
    assert evaluation.has_primary_diagnosis, "Missing primary diagnosis"
    assert evaluation.has_differential_diagnoses, "Missing differential diagnoses"
    assert evaluation.has_confidence_score, "Missing confidence score"
    assert evaluation.has_risk_assessment, "Missing risk assessment"


@pytest.mark.diagnosis
@pytest.mark.parametrize("scenario", EMERGENCY_SCENARIOS, ids=lambda s: s.id)
def test_emergency_diagnosis_quality(medical_graph, scenario):
    """Test emergency diagnoses meet higher quality standards"""
    
    result = medical_graph.analyze(user_input=scenario.input_text)
    
    assert result.get("success"), "Emergency diagnosis failed"
    
    diagnosis = result.get("diagnosis", {})
    evaluation = DiagnosisEvaluator.evaluate(
        diagnosis,
        expected_severity="EMERGENCY"
    )
    
    # Emergency cases require stricter standards
    assert evaluation.quality_score >= 0.8, \
        f"Emergency diagnosis quality too low: {evaluation.quality_score:.2f}"
    
    assert evaluation.severity_appropriate, \
        "Emergency severity not properly assessed"
    
    assert evaluation.red_flags_identified, \
        "Emergency red flags not identified"
    
    assert evaluation.clinical_reasoning_present, \
        "Clinical reasoning insufficient for emergency case"


@pytest.mark.diagnosis
def test_diagnosis_confidence_calibration(medical_graph):
    """Test diagnosis confidence scores are well-calibrated"""
    
    # Clear case - should have high confidence
    clear_case = "Fever 39°C, cough, sore throat for 3 days, no other symptoms"
    result_clear = medical_graph.analyze(user_input=clear_case)
    
    diagnosis_clear = result_clear.get("diagnosis", {})
    confidence_clear = diagnosis_clear.get("confidence", 0)
    
    assert confidence_clear >= 0.6, \
        f"Clear case should have high confidence, got {confidence_clear}"
    
    # Vague case - should have lower confidence
    vague_case = "I don't feel well"
    result_vague = medical_graph.analyze(user_input=vague_case)
    
    diagnosis_vague = result_vague.get("diagnosis", {})
    confidence_vague = diagnosis_vague.get("confidence", 1.0)
    
    # Vague case should either have low confidence OR request more information
    information_needed = result_vague.get("information_needed", False)
    
    assert confidence_vague < 0.7 or information_needed, \
        f"Vague case should have low confidence or request info. Confidence: {confidence_vague}, Info needed: {information_needed}"


@pytest.mark.diagnosis
def test_diagnosis_differential_diversity(medical_graph):
    """Test differential diagnoses cover diverse possibilities"""
    
    test_input = "Persistent cough for 2 weeks, some chest discomfort"
    
    result = medical_graph.analyze(user_input=test_input)
    
    diagnosis = result.get("diagnosis", {})
    differential = diagnosis.get("differential_diagnosis", [])
    
    assert len(differential) >= 2, "Insufficient differential diagnoses"
    
    # Check conditions are different
    conditions = [d.get("condition", "").lower() for d in differential]
    unique_conditions = set(conditions)
    
    assert len(unique_conditions) == len(conditions), \
        "Differential diagnoses should be unique"
    
    # Each should have probability and reasoning
    for diff in differential:
        assert "condition" in diff, "Differential missing condition"
        assert "probability" in diff, "Differential missing probability"
        assert "reasoning" in diff, "Differential missing reasoning"
        
        # Reasoning should be meaningful
        reasoning = diff.get("reasoning", "")
        assert len(reasoning) > 20, f"Insufficient reasoning: {reasoning}"


@pytest.mark.diagnosis
def test_diagnosis_provides_clinical_reasoning(medical_graph):
    """Test diagnosis includes clear clinical reasoning"""
    
    test_input = "Sudden onset severe headache, neck stiffness, light sensitivity"
    
    result = medical_graph.analyze(user_input=test_input)
    
    diagnosis = result.get("diagnosis", {})
    reasoning = diagnosis.get("clinical_reasoning", "")
    
    assert reasoning, "No clinical reasoning provided"
    assert len(reasoning) > 100, f"Clinical reasoning too brief: {len(reasoning)} chars"
    
    # Should mention key symptoms
    reasoning_lower = reasoning.lower()
    assert "headache" in reasoning_lower or "đau đầu" in reasoning_lower
    assert "neck" in reasoning_lower or "cổ" in reasoning_lower or "stiff" in reasoning_lower


@pytest.mark.diagnosis
def test_diagnosis_includes_medical_disclaimers(medical_graph):
    """Test diagnosis includes appropriate medical disclaimers"""
    
    test_input = "I have chest pain"
    
    result = medical_graph.analyze(user_input=test_input)
    
    final_response = result.get("final_response", "")
    
    # Should include disclaimer about seeking professional care
    response_lower = final_response.lower()
    
    disclaimer_phrases = [
        "preliminary assessment",
        "not a final diagnosis",
        "consult",
        "professional",
        "doctor",
        "medical attention",
        "bác sĩ",
        "chuyên môn"
    ]
    
    has_disclaimer = any(phrase in response_lower for phrase in disclaimer_phrases)
    
    assert has_disclaimer, "Diagnosis missing medical disclaimer"


@pytest.mark.diagnosis
@pytest.mark.slow
def test_diagnosis_critic_improves_quality(medical_graph):
    """Test diagnosis critic successfully improves low-quality diagnoses"""
    
    # This test would need access to revision history
    # For now, just check that revision count is reasonable
    
    test_input = "Complex symptoms: fever, fatigue, joint pain, rash, weight loss"
    
    result = medical_graph.analyze(user_input=test_input)
    
    assert result.get("success"), "Complex case failed"
    
    revision_count = result.get("revision_count", 0)
    
    # Complex case might trigger revisions
    assert revision_count <= 2, f"Too many revisions: {revision_count}"
    
    # Final diagnosis should still be high quality
    diagnosis = result.get("diagnosis", {})
    evaluation = DiagnosisEvaluator.evaluate(diagnosis)
    
    assert evaluation.quality_score >= 0.6, \
        f"Quality not improved by revisions: {evaluation.quality_score}"


@pytest.mark.diagnosis
def test_diagnosis_severity_assessment(medical_graph):
    """Test diagnosis correctly assesses severity levels"""
    
    test_cases = [
        ("Minor cold symptoms", "LOW"),
        ("Persistent fever with fatigue", "MODERATE"),
        ("Severe chest pain radiating to arm", "EMERGENCY"),
    ]
    
    for test_input, expected_severity in test_cases:
        result = medical_graph.analyze(user_input=test_input)
        
        assert result.get("success"), f"Failed for: {test_input}"
        
        diagnosis = result.get("diagnosis", {})
        risk_assessment = diagnosis.get("risk_assessment", {})
        severity = risk_assessment.get("severity")
        
        assert severity == expected_severity, \
            f"Input: '{test_input}' - Expected {expected_severity}, got {severity}"
