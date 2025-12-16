from __future__ import annotations
import re
from typing import Tuple, Optional, Dict, List
import pickle

from src.middleware.guardrail_config import get_prompt_injection_detector


def detect_injection_attack(text: str) -> bool:
    if not text:
        return False
    
    text_lower = text.lower()
    text_lower = re.sub(r'\b(ignore|i|just|say|that)\b', '', text_lower)
    text_lower = re.sub(r'\s+', ' ', text_lower).strip()
    print(text_lower)
    prompt_protect = get_prompt_injection_detector()
    return prompt_protect.predict([text_lower])[0] == 1


def check_guardrail_simple( text: str) -> Tuple[bool, Optional[str]]:
    try:
        is_attack = detect_injection_attack(text)
        if is_attack:
            print(f"SECURITY: Blocked injection attack attempt")
            return True, "injection_attack"

        return False, None
        
    except Exception as e:
        # On error, allow message through (fail open for availability)
        print(f"⚠️ Guardrail check error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

__all__ = [
    'check_guardrail_simple',
    'detect_injection_attack'  # Security function
]