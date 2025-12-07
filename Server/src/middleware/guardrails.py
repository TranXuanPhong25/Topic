from __future__ import annotations
import re
from typing import Tuple, Optional, Dict, List

# Basic keyword sets (could be externalized)
NON_MEDICAL_KEYWORDS = [
    # entertainment / unrelated
    "movie", "game", "football", "soccer", "music", "lyrics", "recipe", "cooking",
    "stock", "crypto", "bitcoin", "programming", "code", "travel", "vacation"
]

PRESCRIPTION_KEYWORDS = [
    "prescribe", "thuốc", "dose", "dosage", "mg", "ml", "pill", "tablet", "frequency",
    "how many times", "bao nhiêu lần", "uống bao nhiêu", "take how", "liều"
]

SELF_HARM_KEYWORDS = [
    "suicide", "kill myself", "end my life", "self harm", "hurt myself", "want to die",
    "tự tử", "tự sát", "tự vẫn", "cắt bản thân", "muốn chết", "tôi muốn chết",
    "kết liễu", "kết liễu cuộc đời", "kết thúc cuộc đời", "muốn tự tử", "tự hại", "muốn tự hại"
]

EMERGENCY_KEYWORDS = [
    "chest pain", "shortness of breath", "difficulty breathing", "severe bleeding",
    "stroke", "numb face", "cannot breathe", "loss of consciousness", "sudden weakness",
    "pain in chest", "đau ngực", "khó thở", "chảy máu nhiều"
]

PII_PATTERNS = {
    'email': re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    'phone': re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}"),
    'password': re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE),
}

def _contains_any(text: str, keywords: List[str]) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)

def scrub_pii(text: str) -> Tuple[str, Dict[str, List[str]]]:
    """Redact PII patterns from text. Returns (scrubbed_text, found_metadata)."""
    found: Dict[str, List[str]] = {k: [] for k in PII_PATTERNS.keys()}
    scrubbed = text
    for name, pattern in PII_PATTERNS.items():
        matches = pattern.findall(scrubbed)
        if matches:
            found[name].extend(matches)
            # replace each occurrence with placeholder
            for m in matches:
                scrubbed = scrubbed.replace(m, f"<{name}_redacted>")
    return scrubbed, found

def classify_intent(text: str) -> Optional[str]:
    """Return intent classification tag or None if medical-ish.
    Tags: 'non_medical' currently only.
    """
    if _contains_any(text, NON_MEDICAL_KEYWORDS):
        return 'non_medical'
    return None

def detect_prescription_request(text: str) -> bool:
    return _contains_any(text, PRESCRIPTION_KEYWORDS)

def detect_self_harm(text: str) -> bool:
    return _contains_any(text, SELF_HARM_KEYWORDS)

def detect_emergency(text: str) -> bool:
    return _contains_any(text, EMERGENCY_KEYWORDS)


_VI_CHARS = set("ăâêôơưđáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
_VI_WORDS = {"tôi", "muốn", "không", "có", "bác", "sĩ", "thuốc", "đau", "ngực", "khó", "thở", "vẫn", "tự", "sát"}

def detect_language(text: str) -> str:
    t = text.lower()
    if any(ch in _VI_CHARS for ch in t) or any(w in t for w in _VI_WORDS):
        return 'vi'
    return 'en'

def apply_guardrails(text: str) -> Tuple[bool, Optional[str], str, Dict[str, any]]:
    """Apply guardrail checks to input text.
    Returns: (is_safe, action_tag, sanitized_text, metadata)
    """
    meta: Dict[str, any] = {}
    action: Optional[str] = None

    # Emergency & self-harm take precedence
    if detect_self_harm(text):
        action = 'self_harm'
    elif detect_emergency(text):
        action = 'emergency'
    elif detect_prescription_request(text):
        action = 'prescription'
    else:
        intent = classify_intent(text)
        if intent == 'non_medical':
            action = 'non_medical'

    sanitized, pii_found = scrub_pii(text)
    meta['pii_redacted'] = {k: v for k, v in pii_found.items() if v}

    is_safe = action is None
    return is_safe, action, sanitized, meta


def build_refusal_prompt(action: str, text: Optional[str] = None, lang: Optional[str] = None) -> str:
    """
    Build a localized, safety-focused prompt for an LLM to generate a refusal/assistive message.

    The LLM should:
    - Respond in the requested language (default English, supports Vietnamese 'vi')
    - Avoid prescribing medications, dosages, or treatment schedules
    - Provide crisis guidance for self-harm; emergency guidance for emergencies
    - Be empathetic, concise, and include clear next steps
    - Not add medical diagnoses; encourage seeking professional help

    Returns the prompt string. Use with an LLM: model.generate_content(prompt).
    """
    chosen_lang = lang or (detect_language(text or "") if text is not None else 'en')
    user_text = (text or "").strip()

    # Language headers
    if chosen_lang == 'vi':
        header = (
            "Bạn là trợ lý phòng khám. Hãy trả lời bằng tiếng Việt, ngắn gọn, đồng cảm, an toàn.\n"
            "KHÔNG kê đơn, KHÔNG nêu liều lượng thuốc, KHÔNG chẩn đoán.\n"
        )
        emergency_line = "Nếu nguy cấp, hãy gọi số khẩn cấp địa phương (ví dụ: 115 tại Việt Nam)."
        general_next = "Khuyến khích liên hệ bác sĩ hoặc cơ sở y tế để được hướng dẫn phù hợp."
    else:
        header = (
            "You are a clinic assistant. Reply in English, concise, empathetic, and safe.\n"
            "Do NOT prescribe, mention dosages, or provide treatment schedules.\n"
        )
        emergency_line = "If in immediate danger, call your local emergency number (e.g., 115 in Vietnam)."
        general_next = "Encourage contacting a licensed healthcare professional or local clinic for guidance."

    # Action-specific guidance
    if action == 'self_harm':
        guidance = (
            "Focus on crisis support: advise seeking immediate help, contacting emergency services, "
            "hotlines, or trusted professionals. Reinforce that the user matters. "
            f"{emergency_line}"
        )
    elif action == 'emergency':
        guidance = (
            "Indicate potential medical emergency: advise immediate medical attention or calling emergency services. "
            "Avoid diagnosis; encourage seeking urgent professional care."
        )
    elif action == 'prescription':
        guidance = (
            "Politely refuse to provide prescriptions, dosages, or treatment schedules. "
            f"{general_next}"
        )
    elif action == 'non_medical':
        guidance = (
            "Explain you can only help with medical or health-related questions. "
            "Invite the user to ask about symptoms, general health guidance, or clinic services."
        )
    else:
        guidance = (
            "Provide a safe, general message aligned with clinic assistant role. "
            f"{general_next}"
        )

    prompt = (
        f"{header}\n\n"
        f"User message:\n{user_text}\n\n"
        f"Your task:\n{guidance}\n"
        "Respond in 1–3 sentences, no lists, no medical dosages."
    )

    return prompt

def refusal_message_llm(model, action: str, text: Optional[str] = None, lang: Optional[str] = None) -> str:
    """
    Generate a refusal/assistive message via an LLM using the built prompt.
    Falls back to static localized message if generation fails.
    """
    try:
        prompt = build_refusal_prompt(action, text=text, lang=lang)
        resp = model.generate_content(prompt)
        msg = getattr(resp, 'text', '') or ''
        # Basic sanitation: trim and fallback if empty
        msg = msg.strip()
        if msg:
            return msg
    except Exception:
        pass

__all__ = [
    'apply_guardrails', 'refusal_message', 'build_refusal_prompt', 'refusal_message_llm',
    'scrub_pii', 'detect_emergency', 'detect_self_harm', 'detect_prescription_request', 'classify_intent', 'detect_language'
]