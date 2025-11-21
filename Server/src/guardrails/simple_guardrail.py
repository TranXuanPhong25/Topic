"""
LEVEL 1: Simple Guardrail
- Keyword-based detection
- Basic input/output validation
- Emergency detection
- Profanity filtering
- Quick and lightweight
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GuardrailResult:
    """Result of guardrail check"""
    passed: bool
    reason: Optional[str] = None
    action: Optional[str] = None  # "block", "warn", "redirect", "allow"
    modified_content: Optional[str] = None
    severity: str = "info"  # "info", "warning", "critical"


class SimpleGuardrail:
    """
    Simple keyword-based guardrail system.
    Fast, deterministic, easy to maintain.
    """
    
    # Emergency keywords (multiple languages)
    EMERGENCY_KEYWORDS = [
        # Vietnamese
        "cấp cứu", "khẩn cấp", "nguy kịch", "hôn mê", "đau tim", 
        "đột quỵ", "không thở", "chảy máu nhiều", "tai nạn",
        "ngộ độc", "tự tử", "tự sát", "muốn chết",
        # English
        "emergency", "911", "dying", "heart attack", "stroke",
        "suicide", "can't breathe", "severe bleeding", "unconscious"
    ]
    
    # Medical advice keywords (bot should NOT give)
    MEDICAL_ADVICE_KEYWORDS = [
        "chẩn đoán", "kê đơn", "thuốc gì", "liều lượng thuốc",
        "diagnose", "prescription", "what medicine", "drug dosage",
        "có phải bệnh", "bệnh gì", "có bị ung thư",
        "is it cancer", "what disease"
    ]
    
    # Personal/sensitive data keywords
    SENSITIVE_DATA_KEYWORDS = [
        "số cmnd", "cccd", "thẻ tín dụng", "mật khẩu", "password",
        "credit card", "social security", "bank account",
        "tài khoản ngân hàng"
    ]
    
    # Inappropriate content
    PROFANITY_KEYWORDS = [
        "đồ chó", "địt", "lồn", "fuck", "shit", "damn",
        "ngu", "khốn", "chết tiệt"
    ]
    
    # Scope violations (out of domain)
    OUT_OF_SCOPE_KEYWORDS = [
        "thời tiết", "bóng đá", "chính trị", "tôn giáo",
        "weather", "football", "politics", "religion",
        "nấu ăn", "cooking", "du lịch", "travel"
    ]
    
    def __init__(self):
        """Initialize simple guardrail"""
        self.blocked_count = 0
        self.warned_count = 0
        
    def check_input(self, user_input: str) -> GuardrailResult:
        """
        Check user input before processing
        
        Args:
            user_input: Raw user message
            
        Returns:
            GuardrailResult with pass/fail and action
        """
        user_input_lower = user_input.lower()
        
        # 1. Check for emergencies (highest priority)
        if self._contains_keywords(user_input_lower, self.EMERGENCY_KEYWORDS):
            return GuardrailResult(
                passed=True,  # Allow but redirect
                reason="Emergency detected",
                action="redirect",
                modified_content="🚨 KHẨN CẤP: Vui lòng GỌI 115 hoặc đến bệnh viện gần nhất ngay lập tức!",
                severity="critical"
            )
        
        # 2. Check for profanity
        if self._contains_keywords(user_input_lower, self.PROFANITY_KEYWORDS):
            self.blocked_count += 1
            return GuardrailResult(
                passed=False,
                reason="Inappropriate language detected",
                action="block",
                modified_content="Xin lỗi, tôi không thể xử lý tin nhắn chứa ngôn từ không phù hợp.",
                severity="warning"
            )
        
        # 3. Check for sensitive data (PII protection)
        if self._contains_keywords(user_input_lower, self.SENSITIVE_DATA_KEYWORDS):
            self.warned_count += 1
            return GuardrailResult(
                passed=True,
                reason="Potential sensitive data detected",
                action="warn",
                modified_content=None,  # Allow but log warning
                severity="warning"
            )
        
        # 4. Check for out-of-scope requests
        if self._contains_keywords(user_input_lower, self.OUT_OF_SCOPE_KEYWORDS):
            return GuardrailResult(
                passed=False,
                reason="Out of scope request",
                action="block",
                modified_content="Xin lỗi, tôi chỉ có thể hỗ trợ về các vấn đề y tế và phòng khám. Tôi không thể trả lời câu hỏi này.",
                severity="info"
            )
        
        # 5. Input length validation
        if len(user_input) > 2000:
            return GuardrailResult(
                passed=False,
                reason="Input too long",
                action="block",
                modified_content="Tin nhắn quá dài. Vui lòng rút gọn lại (tối đa 2000 ký tự).",
                severity="info"
            )
        
        if len(user_input.strip()) < 2:
            return GuardrailResult(
                passed=False,
                reason="Input too short",
                action="block",
                modified_content="Vui lòng nhập tin nhắn có nội dung.",
                severity="info"
            )
        
        # All checks passed
        return GuardrailResult(
            passed=True,
            reason="Input validation passed",
            action="allow",
            severity="info"
        )
    
    def check_output(self, bot_response: str, user_input: str) -> GuardrailResult:
        """
        Check bot output before sending to user
        
        Args:
            bot_response: Generated bot response
            user_input: Original user input for context
            
        Returns:
            GuardrailResult with pass/fail and action
        """
        response_lower = bot_response.lower()
        
        # 1. Check if bot is giving medical advice (forbidden)
        medical_advice_patterns = [
            r"bạn (có thể|nên) uống thuốc",
            r"đây là bệnh",
            r"chẩn đoán của bạn là",
            r"you (have|might have)",
            r"(take|use) this (medicine|drug)",
            r"diagnosis is"
        ]
        
        for pattern in medical_advice_patterns:
            if re.search(pattern, response_lower):
                return GuardrailResult(
                    passed=False,
                    reason="Bot attempting to give medical advice",
                    action="block",
                    modified_content="Xin lỗi, tôi không thể đưa ra chẩn đoán hoặc kê đơn thuốc. Vui lòng đặt lịch khám với bác sĩ để được tư vấn chuyên môn.",
                    severity="critical"
                )
        
        # 2. Check response length (too short might be error)
        if len(bot_response.strip()) < 10:
            return GuardrailResult(
                passed=False,
                reason="Response too short (possible error)",
                action="block",
                modified_content="Xin lỗi, tôi gặp sự cố khi tạo phản hồi. Vui lòng thử lại.",
                severity="warning"
            )
        
        # 3. Check for leaked system prompts or technical errors
        system_leakage_keywords = [
            "system:", "assistant:", "you are a", "bạn là một ai",
            "prompt:", "instruction:", "error:", "exception:",
            "traceback", "api_key", "token"
        ]
        
        if self._contains_keywords(response_lower, system_leakage_keywords):
            return GuardrailResult(
                passed=False,
                reason="System information leakage detected",
                action="block",
                modified_content="Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ bộ phận hỗ trợ.",
                severity="critical"
            )
        
        # 4. Check for contact info disclosure (protect staff privacy)
        contact_patterns = [
            r'\b\d{10,11}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b'  # Credit card pattern
        ]
        
        for pattern in contact_patterns:
            if re.search(pattern, bot_response):
                # Allow official clinic contact only
                if "clinic" in user_input.lower() or "phòng khám" in user_input.lower():
                    continue
                
                return GuardrailResult(
                    passed=False,
                    reason="Unauthorized contact information disclosure",
                    action="warn",
                    modified_content=None,
                    severity="warning"
                )
        
        # All checks passed
        return GuardrailResult(
            passed=True,
            reason="Output validation passed",
            action="allow",
            severity="info"
        )
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords"""
        return any(keyword.lower() in text for keyword in keywords)
    
    def get_stats(self) -> Dict:
        """Get guardrail statistics"""
        return {
            "type": "simple",
            "blocked_count": self.blocked_count,
            "warned_count": self.warned_count
        }


# Example usage
if __name__ == "__main__":
    guardrail = SimpleGuardrail()
    
    # Test cases
    test_inputs = [
        "Tôi bị đau tim, cần cấp cứu!",  # Emergency
        "Địt mẹ chatbot",  # Profanity
        "Số CMND của tôi là 123456789",  # Sensitive data
        "Thời tiết hôm nay thế nào?",  # Out of scope
        "Tôi cần đặt lịch khám",  # Normal
    ]
    
    for inp in test_inputs:
        result = guardrail.check_input(inp)
        print(f"\nInput: {inp}")
        print(f"Result: {result}")
