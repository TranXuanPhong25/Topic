from src.middleware.guardrails import apply_guardrails, refusal_message

def test_non_medical_detection():
    safe, action, sanitized, meta = apply_guardrails("I love playing football and coding games")
    assert not safe and action == 'non_medical'
    assert 'football' in sanitized.lower()
    assert refusal_message(action).startswith("I can only help")

def test_prescription_block():
    text = "Can you prescribe amoxicillin 500mg twice daily?"
    safe, action, sanitized, meta = apply_guardrails(text)
    assert not safe and action == 'prescription'
    assert '<email_redacted>' not in sanitized  # no email here

def test_self_harm_detection():
    safe, action, sanitized, meta = apply_guardrails("I feel like I want to kill myself")
    assert not safe and action == 'self_harm'
    assert 'help' in refusal_message(action).lower()

def test_emergency_detection():
    safe, action, sanitized, meta = apply_guardrails("I have chest pain and shortness of breath")
    assert not safe and action == 'emergency'

def test_pii_scrubbing_email_phone():
    text = "My email is test.user@example.com and phone +1-202-555-0145 please advise about headache"
    safe, action, sanitized, meta = apply_guardrails(text)
    # Should still be medical (headache) but PII redacted
    assert safe and action is None
    assert 'example.com' not in sanitized
    assert '<email_redacted>' in sanitized
    assert any(v for v in meta.get('pii_redacted', {}).values())


def test_self_harm_vietnamese_priority_over_prescription():
    text = "tôi muốn tự vẫn, có thuốc nào không"
    safe, action, sanitized, meta = apply_guardrails(text)
    assert not safe and action == 'self_harm'
    assert 'help' in refusal_message(action).lower()

