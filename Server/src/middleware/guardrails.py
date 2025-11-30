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

REFUSALS = {
    'non_medical': (
        "I can only help with medical or health-related questions. "
        "Please ask about symptoms, general health guidance, or clinic services."
    ),
    'prescription': (
        "I can't provide prescriptions, specific medication dosages, or treatment schedules. "
        "Please consult a licensed healthcare professional for medication guidance."
    ),
    'self_harm': (
        "If you're thinking about self-harm or suicide, please seek immediate help. "
        "Contact local emergency services or a trusted professional right now. You matter. "
        "If you're in immediate danger, call your local emergency number (for example, 115 in Vietnam)."
    ),
    'emergency': (
        "Your description may indicate a medical emergency. Please seek immediate medical attention or call emergency services."
    ),
}

# Localized refusal messages (English default + Vietnamese)
REFUSALS_L10N: Dict[str, Dict[str, str]] = {
    'non_medical': {
        'en': (
            "I can only help with medical or health-related questions. "
            "Please ask about symptoms, general health guidance, or clinic services."
        ),
        'vi': (
            "Mình chỉ hỗ trợ các câu hỏi liên quan đến y tế/sức khỏe. "
            "Vui lòng hỏi về triệu chứng, hướng dẫn sức khỏe chung, hoặc dịch vụ của phòng khám."
        ),
    },
    'prescription': {
        'en': (
            "I can't provide prescriptions, specific medication dosages, or treatment schedules. "
            "Please consult a licensed healthcare professional for medication guidance."
        ),
        'vi': (
            "Mình không thể kê đơn, cung cấp liều lượng thuốc hay lịch điều trị. "
            "Vui lòng trao đổi với bác sĩ/nhân viên y tế được cấp phép để được hướng dẫn về thuốc."
        ),
    },
    'self_harm': {
        'en': (
            "If you're thinking about self-harm or suicide, please seek immediate help. "
            "Contact local emergency services or a trusted professional right now. You matter. "
            "If you're in immediate danger, call your local emergency number (for example, 115 in Vietnam)."
        ),
        'vi': (
            "Nếu bạn đang nghĩ đến việc tự hại hoặc tự tử, hãy tìm sự giúp đỡ ngay lập tức. "
            "Hãy liên hệ dịch vụ khẩn cấp hoặc một chuyên gia đáng tin cậy ngay bây giờ. Bạn rất quan trọng. "
            "Nếu bạn đang trong tình huống nguy cấp, hãy gọi số khẩn cấp địa phương (ví dụ: 115 tại Việt Nam)."
        ),
    },
    'emergency': {
        'en': (
            "Your description may indicate a medical emergency. Please seek immediate medical attention or call emergency services."
        ),
        'vi': (
            "Mô tả của bạn có thể cho thấy tình huống khẩn cấp. Hãy tìm trợ giúp y tế ngay hoặc gọi dịch vụ khẩn cấp."
        ),
    },
}

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

def refusal_message(action: str, text: Optional[str] = None, lang: Optional[str] = None) -> str:
    # Prefer new localized set; fall back to legacy defaults
    chosen_lang = lang or (detect_language(text) if text else 'en')
    if action in REFUSALS_L10N:
        return REFUSALS_L10N[action].get(chosen_lang, REFUSALS_L10N[action]['en'])
    return REFUSALS.get(action, "I'm unable to process this request.")

__all__ = [
    'apply_guardrails', 'refusal_message', 'scrub_pii', 'detect_emergency',
    'detect_self_harm', 'detect_prescription_request', 'classify_intent', 'detect_language'
]