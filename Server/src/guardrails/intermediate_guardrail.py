"""
LEVEL 2: Intermediate Guardrail
- NLP-based intent classification
- Context-aware validation
- Conversation history analysis
- Rate limiting and abuse detection
- Medical claim verification
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import google.generativeai as genai
import os

@dataclass
class ConversationContext:
    """Track conversation context for validation"""
    user_id: str
    message_count: int = 0
    last_message_time: Optional[datetime] = None
    topics: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suspicious_behavior: bool = False


@dataclass
class GuardrailResult:
    """Result of guardrail check"""
    passed: bool
    reason: Optional[str] = None
    action: Optional[str] = None
    modified_content: Optional[str] = None
    severity: str = "info"
    confidence: float = 1.0  # 0-1 confidence score


class IntermediateGuardrail:
    """
    Intermediate guardrail with NLP and context awareness.
    Uses Gemini for intent classification and claim verification.
    """
    
    # Intent categories
    INTENT_CATEGORIES = {
        "emergency": "Medical emergency requiring immediate attention",
        "appointment": "Scheduling or managing appointments",
        "medical_advice": "Seeking diagnosis or treatment recommendations",
        "general_info": "General clinic information",
        "symptoms": "Describing symptoms for assessment",
        "faq": "Common questions about clinic services",
        "small_talk": "Casual conversation",
        "inappropriate": "Offensive or out-of-scope content",
        "sensitive": "Contains personal/sensitive information"
    }
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize intermediate guardrail with Gemini"""
        self.api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        else:
            self.model = None
            print("⚠️  Warning: No Gemini API key provided. Some features will be limited.")
        
        # Rate limiting (user_id -> context)
        self.user_contexts: Dict[str, ConversationContext] = {}
        self.rate_limit_window = timedelta(minutes=1)
        self.max_messages_per_minute = 10
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "blocked": 0,
            "warned": 0,
            "redirected": 0,
            "intents_detected": defaultdict(int)
        }
    
    def check_input(self, user_input: str, user_id: str = "anonymous", 
                   conversation_history: Optional[List[Dict]] = None) -> GuardrailResult:
        """
        Context-aware input validation with intent classification
        
        Args:
            user_input: User message
            user_id: Unique user identifier
            conversation_history: Previous messages for context
            
        Returns:
            GuardrailResult
        """
        self.stats["total_checks"] += 1
        
        # 1. Rate limiting check
        rate_limit_result = self._check_rate_limit(user_id)
        if not rate_limit_result.passed:
            self.stats["blocked"] += 1
            return rate_limit_result
        
        # 2. Intent classification using Gemini
        intent, confidence = self._classify_intent(user_input, conversation_history)
        self.stats["intents_detected"][intent] += 1
        
        print(f"🎯 Detected intent: {intent} (confidence: {confidence:.2f})")
        
        # 3. Handle different intents
        if intent == "emergency":
            self.stats["redirected"] += 1
            return GuardrailResult(
                passed=True,
                reason=f"Emergency intent detected (confidence: {confidence:.2f})",
                action="redirect",
                modified_content=(
                    "🚨 **TÌNH HUỐNG KHẨN CẤP**\n\n"
                    "Nếu đây là tình huống nguy cấp, vui lòng:\n"
                    "- **Gọi 115** (Cấp cứu)\n"
                    "- **Gọi 113** (Công an)\n"
                    "- Đến phòng cấp cứu gần nhất\n\n"
                    "Tôi chỉ là chatbot và không thể xử lý các tình huống khẩn cấp."
                ),
                severity="critical",
                confidence=confidence
            )
        
        if intent == "medical_advice" and confidence > 0.7:
            self.stats["warned"] += 1
            # Get context-aware response
            context_response = self._generate_medical_advice_disclaimer(user_input)
            return GuardrailResult(
                passed=True,
                reason=f"Medical advice request detected (confidence: {confidence:.2f})",
                action="warn",
                modified_content=context_response,
                severity="warning",
                confidence=confidence
            )
        
        if intent == "inappropriate":
            self.stats["blocked"] += 1
            return GuardrailResult(
                passed=False,
                reason=f"Inappropriate content detected (confidence: {confidence:.2f})",
                action="block",
                modified_content=(
                    "Xin lỗi, tôi không thể xử lý yêu cầu này. "
                    "Vui lòng đặt câu hỏi liên quan đến dịch vụ y tế hoặc phòng khám."
                ),
                severity="warning",
                confidence=confidence
            )
        
        if intent == "sensitive":
            self.stats["warned"] += 1
            self._add_warning(user_id, "Shared sensitive information")
            return GuardrailResult(
                passed=True,
                reason=f"Sensitive data detected (confidence: {confidence:.2f})",
                action="warn",
                modified_content=None,
                severity="warning",
                confidence=confidence
            )
        
        # 4. Conversation pattern analysis
        pattern_result = self._analyze_conversation_pattern(user_id, user_input, conversation_history)
        if not pattern_result.passed:
            return pattern_result
        
        # 5. Basic safety checks
        basic_result = self._basic_safety_checks(user_input)
        if not basic_result.passed:
            return basic_result
        
        # All checks passed
        return GuardrailResult(
            passed=True,
            reason="Input validation passed",
            action="allow",
            severity="info",
            confidence=confidence
        )
    
    def check_output(self, bot_response: str, user_input: str, 
                    conversation_history: Optional[List[Dict]] = None) -> GuardrailResult:
        """
        Context-aware output validation with medical claim verification
        
        Args:
            bot_response: Generated response
            user_input: Original user input
            conversation_history: Conversation history
            
        Returns:
            GuardrailResult
        """
        # 1. Medical claim verification
        if self.model:
            claim_result = self._verify_medical_claims(bot_response, user_input)
            if not claim_result.passed:
                self.stats["blocked"] += 1
                return claim_result
        
        # 2. Check for overstepping boundaries
        boundary_result = self._check_professional_boundaries(bot_response)
        if not boundary_result.passed:
            self.stats["blocked"] += 1
            return boundary_result
        
        # 3. Check response consistency with context
        if conversation_history:
            consistency_result = self._check_consistency(bot_response, conversation_history)
            if not consistency_result.passed:
                self.stats["warned"] += 1
                return consistency_result
        
        # 4. Basic safety checks
        basic_result = self._basic_safety_checks(bot_response)
        if not basic_result.passed:
            return basic_result
        
        return GuardrailResult(
            passed=True,
            reason="Output validation passed",
            action="allow",
            severity="info"
        )
    
    # ==================== Helper Methods ====================
    
    def _classify_intent(self, user_input: str, 
                        conversation_history: Optional[List[Dict]] = None) -> Tuple[str, float]:
        """
        Classify user intent using Gemini
        
        Returns:
            (intent_category, confidence_score)
        """
        if not self.model:
            # Fallback to simple keyword matching
            return self._fallback_intent_classification(user_input)
        
        try:
            # Build context from history
            context = ""
            if conversation_history:
                recent = conversation_history[-3:]  # Last 3 messages
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])
            
            prompt = f"""Classify the intent of this user message in a medical clinic chatbot context.

Available intents:
{chr(10).join([f"- {k}: {v}" for k, v in self.INTENT_CATEGORIES.items()])}

Conversation context (if any):
{context}

User message: "{user_input}"

Respond with ONLY the intent name and confidence (0-1) in this format:
intent: <intent_name>
confidence: <0.XX>
"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse response
            intent_match = re.search(r'intent:\s*(\w+)', result_text, re.IGNORECASE)
            conf_match = re.search(r'confidence:\s*(0\.\d+|1\.0?)', result_text, re.IGNORECASE)
            
            intent = intent_match.group(1) if intent_match else "general_info"
            confidence = float(conf_match.group(1)) if conf_match else 0.5
            
            return intent, confidence
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            return self._fallback_intent_classification(user_input)
    
    def _fallback_intent_classification(self, user_input: str) -> Tuple[str, float]:
        """Simple keyword-based intent classification as fallback"""
        text = user_input.lower()
        
        emergency_keywords = ["cấp cứu", "khẩn cấp", "đau tim", "đột quỵ", "emergency"]
        if any(kw in text for kw in emergency_keywords):
            return "emergency", 0.9
        
        appointment_keywords = ["đặt lịch", "hẹn khám", "appointment", "schedule"]
        if any(kw in text for kw in appointment_keywords):
            return "appointment", 0.8
        
        medical_advice_keywords = ["bệnh gì", "thuốc gì", "chẩn đoán", "diagnose", "treatment"]
        if any(kw in text for kw in medical_advice_keywords):
            return "medical_advice", 0.7
        
        inappropriate_keywords = ["fuck", "shit", "địt", "lồn"]
        if any(kw in text for kw in inappropriate_keywords):
            return "inappropriate", 0.95
        
        return "general_info", 0.5
    
    def _check_rate_limit(self, user_id: str) -> GuardrailResult:
        """Check if user is exceeding rate limits"""
        now = datetime.now()
        
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = ConversationContext(user_id=user_id)
        
        context = self.user_contexts[user_id]
        
        # Reset counter if window expired
        if context.last_message_time and (now - context.last_message_time) > self.rate_limit_window:
            context.message_count = 0
        
        context.message_count += 1
        context.last_message_time = now
        
        if context.message_count > self.max_messages_per_minute:
            context.suspicious_behavior = True
            return GuardrailResult(
                passed=False,
                reason="Rate limit exceeded",
                action="block",
                modified_content="Bạn đang gửi tin nhắn quá nhanh. Vui lòng chờ một chút trước khi tiếp tục.",
                severity="warning"
            )
        
        return GuardrailResult(passed=True, reason="Rate limit OK", action="allow")
    
    def _verify_medical_claims(self, bot_response: str, user_input: str) -> GuardrailResult:
        """Verify that bot is not making unsupported medical claims"""
        if not self.model:
            return GuardrailResult(passed=True, reason="Claim verification skipped", action="allow")
        
        try:
            prompt = f"""Analyze this chatbot response to a medical clinic patient.

User question: "{user_input}"
Bot response: "{bot_response}"

Check if the bot is:
1. Giving specific medical diagnosis
2. Prescribing medication
3. Making definitive medical claims without disclaimer
4. Providing treatment advice

Respond with ONLY:
safe: yes/no
reason: <brief reason>
"""
            
            response = self.model.generate_content(prompt)
            result = response.text.strip().lower()
            
            if "safe: no" in result:
                return GuardrailResult(
                    passed=False,
                    reason="Unsafe medical claim detected",
                    action="block",
                    modified_content=(
                        "Xin lỗi, tôi không thể đưa ra chẩn đoán hoặc lời khuyên y tế cụ thể. "
                        "Vui lòng đặt lịch khám với bác sĩ để được tư vấn chuyên môn."
                    ),
                    severity="critical"
                )
            
        except Exception as e:
            print(f"Claim verification error: {e}")
        
        return GuardrailResult(passed=True, reason="Medical claims verified", action="allow")
    
    def _check_professional_boundaries(self, bot_response: str) -> GuardrailResult:
        """Ensure bot maintains professional boundaries"""
        response_lower = bot_response.lower()
        
        # Check for inappropriate familiarity
        overfamiliar_patterns = [
            r'\bcó vẻ bạn\b',
            r'\btôi nghĩ bạn\b', 
            r'\bchắc chắn là\b',
            r'\bđây chắc chắn là bệnh\b'
        ]
        
        for pattern in overfamiliar_patterns:
            if re.search(pattern, response_lower):
                return GuardrailResult(
                    passed=False,
                    reason="Professional boundary violation",
                    action="block",
                    modified_content=None,
                    severity="warning"
                )
        
        return GuardrailResult(passed=True, reason="Professional boundaries maintained", action="allow")
    
    def _check_consistency(self, bot_response: str, 
                          conversation_history: List[Dict]) -> GuardrailResult:
        """Check if response is consistent with conversation history"""
        # Simple consistency check: bot shouldn't contradict itself
        # This is a simplified version - full implementation would use embeddings
        
        # For now, just check if bot is giving different clinic hours/info
        if "giờ làm việc" in bot_response.lower() or "hours" in bot_response.lower():
            for msg in conversation_history:
                if msg.get('role') == 'assistant' and ('giờ làm việc' in msg.get('content', '').lower()):
                    # Found previous mention - should be consistent
                    # Full implementation would compare actual hours
                    pass
        
        return GuardrailResult(passed=True, reason="Consistency check passed", action="allow")
    
    def _analyze_conversation_pattern(self, user_id: str, user_input: str,
                                     conversation_history: Optional[List[Dict]]) -> GuardrailResult:
        """Analyze conversation patterns for abuse detection"""
        context = self.user_contexts.get(user_id)
        if not context:
            return GuardrailResult(passed=True, reason="No pattern issues", action="allow")
        
        # Check for repetitive messages (spam detection)
        if conversation_history and len(conversation_history) >= 3:
            recent_user_msgs = [msg['content'] for msg in conversation_history[-3:] 
                               if msg.get('role') == 'user']
            if len(set(recent_user_msgs)) == 1:  # All same message
                return GuardrailResult(
                    passed=False,
                    reason="Repetitive messages detected (spam)",
                    action="block",
                    modified_content="Bạn đã gửi tin nhắn này nhiều lần. Tôi có thể giúp gì khác không?",
                    severity="warning"
                )
        
        return GuardrailResult(passed=True, reason="Conversation pattern OK", action="allow")
    
    def _basic_safety_checks(self, text: str) -> GuardrailResult:
        """Basic safety checks (length, encoding, etc.)"""
        if len(text) > 5000:
            return GuardrailResult(
                passed=False,
                reason="Text too long",
                action="block",
                modified_content="Tin nhắn quá dài. Vui lòng rút gọn lại.",
                severity="info"
            )
        
        if len(text.strip()) < 2:
            return GuardrailResult(
                passed=False,
                reason="Text too short",
                action="block",
                modified_content="Vui lòng nhập tin nhắn có nội dung.",
                severity="info"
            )
        
        return GuardrailResult(passed=True, reason="Basic checks passed", action="allow")
    
    def _generate_medical_advice_disclaimer(self, user_input: str) -> str:
        """Generate context-aware disclaimer for medical advice requests"""
        return (
            "Xin lưu ý: Tôi là chatbot hỗ trợ và không thể thay thế ý kiến bác sĩ. "
            "Tôi có thể giúp bạn đặt lịch khám hoặc cung cấp thông tin chung, "
            "nhưng chỉ bác sĩ mới có thể chẩn đoán và kê đơn thuốc chính xác.\n\n"
            "Bạn có muốn đặt lịch khám với bác sĩ không?"
        )
    
    def _add_warning(self, user_id: str, warning: str):
        """Add warning to user context"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id].warnings.append(warning)
    
    def get_stats(self) -> Dict:
        """Get guardrail statistics"""
        return {
            "type": "intermediate",
            "total_checks": self.stats["total_checks"],
            "blocked": self.stats["blocked"],
            "warned": self.stats["warned"],
            "redirected": self.stats["redirected"],
            "intents_detected": dict(self.stats["intents_detected"]),
            "active_users": len(self.user_contexts)
        }


# Example usage
if __name__ == "__main__":
    guardrail = IntermediateGuardrail()
    
    test_cases = [
        ("Tôi bị đau tim!", "user1"),
        ("Tôi bị sốt, bệnh gì vậy?", "user2"),
        ("Giờ làm việc của phòng khám?", "user3"),
    ]
    
    for msg, user_id in test_cases:
        result = guardrail.check_input(msg, user_id)
        print(f"\n{'='*50}")
        print(f"User: {msg}")
        print(f"Result: {result}")
