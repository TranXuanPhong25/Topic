"""
LEVEL 3: Advanced Guardrail System
- Multi-layer AI validation
- HIPAA/GDPR compliance checks
- Semantic safety scoring
- Adversarial prompt detection
- Real-time monitoring and alerting
- Conversation quality assessment
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from collections import defaultdict, deque

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

import os


class RiskLevel(Enum):
    """Risk levels for guardrail violations"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Compliance standards to check"""
    HIPAA = "hipaa"
    GDPR = "gdpr"
    GENERAL_SAFETY = "general_safety"
    MEDICAL_ETHICS = "medical_ethics"


@dataclass
class GuardrailResult:
    """Comprehensive guardrail result"""
    passed: bool
    reason: Optional[str] = None
    action: Optional[str] = None
    modified_content: Optional[str] = None
    severity: str = "info"
    confidence: float = 1.0
    risk_level: RiskLevel = RiskLevel.SAFE
    compliance_violations: List[str] = field(default_factory=list)
    safety_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationQualityMetrics:
    """Metrics for conversation quality"""
    coherence_score: float = 0.0
    helpfulness_score: float = 0.0
    safety_score: float = 0.0
    professionalism_score: float = 0.0
    overall_score: float = 0.0


@dataclass
class UserRiskProfile:
    """Risk profile for a user"""
    user_id: str
    risk_score: float = 0.0
    violation_count: int = 0
    warnings: List[Dict] = field(default_factory=list)
    blocked_count: int = 0
    suspicious_patterns: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class AdvancedGuardrail:
    """
    Advanced multi-layer guardrail system with AI-powered validation,
    compliance checking, and comprehensive safety monitoring.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None, enable_logging: bool = True):
        """
        Initialize advanced guardrail system
        
        Args:
            gemini_api_key: API key for Gemini (optional)
            enable_logging: Enable detailed logging
        """
        self.api_key = gemini_api_key or os.getenv("GOOGLE_API_KEY")
        self.enable_logging = enable_logging
        
        # Initialize Gemini models
        if self.api_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            # Use two models: fast one for quick checks, thorough one for deep analysis
            self.fast_model = genai.GenerativeModel('gemini-2.0-flash-lite')
            self.thorough_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        else:
            self.fast_model = None
            self.thorough_model = None
            print("⚠️  Warning: Gemini not available. Advanced features will be limited.")
        
        # User risk profiles
        self.user_profiles: Dict[str, UserRiskProfile] = {}
        
        # Conversation quality tracking
        self.quality_metrics: Dict[str, List[ConversationQualityMetrics]] = defaultdict(list)
        
        # Incident log for compliance
        self.incident_log: deque = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "risk_levels": defaultdict(int),
            "compliance_violations": defaultdict(int),
            "adversarial_attempts": 0,
            "pii_detected": 0
        }
        
        # Adversarial patterns (continuously updated)
        self.adversarial_patterns = self._load_adversarial_patterns()
        
        # PII patterns (HIPAA/GDPR)
        self.pii_patterns = self._compile_pii_patterns()
        
    def check_input(self, 
                   user_input: str,
                   user_id: str = "anonymous",
                   conversation_history: Optional[List[Dict]] = None,
                   user_metadata: Optional[Dict] = None) -> GuardrailResult:
        """
        Comprehensive multi-layer input validation
        
        Args:
            user_input: User message
            user_id: Unique user identifier
            conversation_history: Previous messages
            user_metadata: Additional user context
            
        Returns:
            Comprehensive GuardrailResult
        """
        self.stats["total_checks"] += 1
        start_time = datetime.now()
        
        # Initialize user profile if needed
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserRiskProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        profile.last_activity = datetime.now()
        
        # Layer 1: Fast heuristic checks (< 10ms)
        fast_result = self._layer1_fast_checks(user_input, profile)
        if not fast_result.passed:
            self._log_incident(user_id, "fast_check_failed", fast_result)
            return fast_result
        
        # Layer 2: PII and compliance checks (< 50ms)
        compliance_result = self._layer2_compliance_checks(user_input, profile)
        if not compliance_result.passed:
            self._log_incident(user_id, "compliance_violation", compliance_result)
            return compliance_result
        
        # Layer 3: Adversarial detection (< 100ms)
        adversarial_result = self._layer3_adversarial_detection(user_input, conversation_history)
        if not adversarial_result.passed:
            self._log_incident(user_id, "adversarial_attempt", adversarial_result)
            profile.suspicious_patterns.append("adversarial_attempt")
            self.stats["adversarial_attempts"] += 1
            return adversarial_result
        
        # Layer 4: AI-powered semantic analysis (< 500ms)
        if self.fast_model:
            semantic_result = self._layer4_semantic_analysis(
                user_input, conversation_history, profile
            )
            if not semantic_result.passed:
                self._log_incident(user_id, "semantic_violation", semantic_result)
                return semantic_result
        
        # Layer 5: Risk scoring and profile update
        risk_score = self._calculate_risk_score(user_input, profile, conversation_history)
        profile.risk_score = risk_score
        
        # Update risk level in result
        risk_level = self._risk_score_to_level(risk_score)
        self.stats["risk_levels"][risk_level.value] += 1
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # All layers passed
        return GuardrailResult(
            passed=True,
            reason="All validation layers passed",
            action="allow",
            severity="info",
            risk_level=risk_level,
            safety_scores={
                "overall_risk": risk_score,
                "user_risk": profile.risk_score,
                "processing_time_ms": processing_time
            },
            metadata={
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "layers_checked": 5
            }
        )
    
    def check_output(self,
                    bot_response: str,
                    user_input: str,
                    user_id: str = "anonymous",
                    conversation_history: Optional[List[Dict]] = None) -> GuardrailResult:
        """
        Comprehensive output validation with quality assessment
        
        Args:
            bot_response: Generated bot response
            user_input: Original user input
            user_id: User identifier
            conversation_history: Conversation history
            
        Returns:
            GuardrailResult with quality metrics
        """
        # Layer 1: Fast safety checks
        fast_result = self._layer1_output_safety(bot_response)
        if not fast_result.passed:
            self._log_incident(user_id, "unsafe_output", fast_result)
            return fast_result
        
        # Layer 2: Medical compliance (HIPAA, ethical boundaries)
        medical_result = self._layer2_medical_compliance(bot_response, user_input)
        if not medical_result.passed:
            self._log_incident(user_id, "medical_compliance_violation", medical_result)
            return medical_result
        
        # Layer 3: Quality assessment (if AI available)
        quality_metrics = ConversationQualityMetrics()
        if self.thorough_model:
            quality_metrics = self._assess_conversation_quality(
                bot_response, user_input, conversation_history
            )
            
            # Store metrics for analysis
            self.quality_metrics[user_id].append(quality_metrics)
            
            # Block if quality is too low
            if quality_metrics.overall_score < 0.4:
                return GuardrailResult(
                    passed=False,
                    reason="Response quality too low",
                    action="block",
                    modified_content="Xin lỗi, tôi cần suy nghĩ lại câu trả lời. Vui lòng thử lại.",
                    severity="warning",
                    risk_level=RiskLevel.MEDIUM,
                    safety_scores={
                        "quality_score": quality_metrics.overall_score,
                        "coherence": quality_metrics.coherence_score,
                        "helpfulness": quality_metrics.helpfulness_score
                    }
                )
        
        # All checks passed
        return GuardrailResult(
            passed=True,
            reason="Output validation passed",
            action="allow",
            severity="info",
            risk_level=RiskLevel.SAFE,
            safety_scores={
                "coherence": quality_metrics.coherence_score,
                "helpfulness": quality_metrics.helpfulness_score,
                "safety": quality_metrics.safety_score,
                "professionalism": quality_metrics.professionalism_score,
                "overall": quality_metrics.overall_score
            }
        )
    
    # ==================== Layer 1: Fast Checks ====================
    
    def _layer1_fast_checks(self, text: str, profile: UserRiskProfile) -> GuardrailResult:
        """Layer 1: Fast heuristic checks (< 10ms)"""
        
        # Length validation
        if len(text) > 5000:
            return GuardrailResult(
                passed=False,
                reason="Input too long",
                action="block",
                modified_content="Tin nhắn quá dài (tối đa 5000 ký tự).",
                risk_level=RiskLevel.LOW
            )
        
        if len(text.strip()) < 2:
            return GuardrailResult(
                passed=False,
                reason="Input too short",
                action="block",
                modified_content="Vui lòng nhập tin nhắn có nội dung.",
                risk_level=RiskLevel.LOW
            )
        
        # Rate limiting based on user risk
        max_rate = 20 if profile.risk_score < 0.3 else 10
        # Implementation would check actual rate here
        
        # Emergency keywords (fast path to redirect)
        emergency_keywords = [
            "cấp cứu", "khẩn cấp", "đau tim", "đột quỵ", "không thở",
            "emergency", "heart attack", "stroke", "can't breathe"
        ]
        text_lower = text.lower()
        if any(kw in text_lower for kw in emergency_keywords):
            return GuardrailResult(
                passed=True,
                reason="Emergency detected - redirect",
                action="redirect",
                modified_content=(
                    "🚨 **KHẨN CẤP**\n\n"
                    "Nếu đây là tình huống cấp cứu:\n"
                    "- Gọi **115** (Cấp cứu)\n"
                    "- Gọi **113** (Công an)\n"
                    "- Đến bệnh viện gần nhất\n\n"
                    "Chatbot không thể xử lý tình huống khẩn cấp."
                ),
                severity="critical",
                risk_level=RiskLevel.CRITICAL
            )
        
        # Profanity check
        profanity_keywords = ["fuck", "shit", "địt", "lồn", "chó", "khốn"]
        if any(kw in text_lower for kw in profanity_keywords):
            profile.violation_count += 1
            return GuardrailResult(
                passed=False,
                reason="Inappropriate language",
                action="block",
                modified_content="Vui lòng sử dụng ngôn từ lịch sự.",
                risk_level=RiskLevel.MEDIUM
            )
        
        return GuardrailResult(passed=True, reason="Fast checks passed", action="allow")
    
    # ==================== Layer 2: Compliance ====================
    
    def _layer2_compliance_checks(self, text: str, profile: UserRiskProfile) -> GuardrailResult:
        """Layer 2: HIPAA/GDPR compliance checks (< 50ms)"""
        violations = []
        
        # Check for PII (Personal Identifiable Information)
        pii_detected = self._detect_pii(text)
        
        if pii_detected:
            self.stats["pii_detected"] += 1
            violations.append("PII_DISCLOSURE")
            
            # Log warning but allow (with sanitization in production)
            profile.warnings.append({
                "type": "pii_detected",
                "timestamp": datetime.now().isoformat(),
                "details": pii_detected
            })
            
            return GuardrailResult(
                passed=True,  # Allow but warn
                reason=f"PII detected: {', '.join(pii_detected)}",
                action="warn",
                severity="warning",
                risk_level=RiskLevel.MEDIUM,
                compliance_violations=violations,
                metadata={"pii_types": pii_detected}
            )
        
        return GuardrailResult(
            passed=True,
            reason="Compliance checks passed",
            action="allow",
            compliance_violations=[]
        )
    
    def _detect_pii(self, text: str) -> List[str]:
        """Detect Personal Identifiable Information"""
        detected = []
        
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(text):
                detected.append(pii_type)
        
        return detected
    
    def _compile_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection"""
        return {
            "phone_number": re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            "id_number": re.compile(r'\b\d{9,12}\b'),  # CCCD/CMND
            "address": re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|đường|phố)\b', re.IGNORECASE)
        }
    
    # ==================== Layer 3: Adversarial Detection ====================
    
    def _layer3_adversarial_detection(self, text: str, 
                                     conversation_history: Optional[List[Dict]]) -> GuardrailResult:
        """Layer 3: Detect adversarial/jailbreak attempts (< 100ms)"""
        
        # Check for known adversarial patterns
        for pattern_name, pattern in self.adversarial_patterns.items():
            if pattern.search(text.lower()):
                return GuardrailResult(
                    passed=False,
                    reason=f"Adversarial pattern detected: {pattern_name}",
                    action="block",
                    modified_content="Yêu cầu không hợp lệ. Vui lòng đặt câu hỏi thông thường.",
                    severity="warning",
                    risk_level=RiskLevel.HIGH,
                    metadata={"adversarial_pattern": pattern_name}
                )
        
        # Check for prompt injection attempts
        injection_indicators = [
            "ignore previous", "forget all", "new instructions",
            "you are now", "system:", "assistant:",
            "bỏ qua", "quên tất cả", "hướng dẫn mới"
        ]
        
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in injection_indicators):
            return GuardrailResult(
                passed=False,
                reason="Prompt injection attempt detected",
                action="block",
                modified_content="Yêu cầu không hợp lệ.",
                severity="warning",
                risk_level=RiskLevel.HIGH
            )
        
        return GuardrailResult(passed=True, reason="No adversarial patterns detected", action="allow")
    
    def _load_adversarial_patterns(self) -> Dict[str, re.Pattern]:
        """Load adversarial attack patterns"""
        return {
            "role_play_attack": re.compile(r'(pretend|act as|you are now|bạn giờ là|giả vờ)', re.IGNORECASE),
            "instruction_override": re.compile(r'(ignore|forget|disregard|bỏ qua|quên).{0,20}(instruction|rule|guideline|previous)', re.IGNORECASE),
            "jailbreak": re.compile(r'(jailbreak|dan mode|developer mode|sudo|root)', re.IGNORECASE),
            "system_prompt_leak": re.compile(r'(show|reveal|tell me).{0,20}(system prompt|instructions|rules)', re.IGNORECASE)
        }
    
    # ==================== Layer 4: Semantic Analysis ====================
    
    def _layer4_semantic_analysis(self, text: str, 
                                  conversation_history: Optional[List[Dict]],
                                  profile: UserRiskProfile) -> GuardrailResult:
        """Layer 4: AI-powered semantic safety analysis (< 500ms)"""
        
        if not self.fast_model:
            return GuardrailResult(passed=True, reason="Semantic analysis skipped", action="allow")
        
        try:
            # Build context
            context = ""
            if conversation_history:
                recent = conversation_history[-3:]
                context = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in recent])
            
            prompt = f"""Analyze this message in a medical chatbot context for safety issues.

Conversation context:
{context}

User message: "{text}"

Check for:
1. Hidden malicious intent
2. Social engineering attempts
3. Requests to bypass safety measures
4. Inappropriate medical advice seeking
5. Harassment or abuse

Respond with JSON:
{{
  "safe": true/false,
  "risk_level": "safe/low/medium/high/critical",
  "issues": ["list of issues found"],
  "confidence": 0.0-1.0
}}
"""
            
            response = self.fast_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                
                if not result.get("safe", True):
                    issues = result.get("issues", [])
                    risk_level_str = result.get("risk_level", "medium")
                    confidence = result.get("confidence", 0.5)
                    
                    return GuardrailResult(
                        passed=False,
                        reason=f"Semantic safety issues: {', '.join(issues)}",
                        action="block",
                        modified_content="Yêu cầu không phù hợp. Tôi chỉ có thể hỗ trợ các vấn đề y tế hợp lệ.",
                        severity="warning",
                        risk_level=RiskLevel[risk_level_str.upper()],
                        confidence=confidence,
                        metadata={"issues": issues}
                    )
            
        except Exception as e:
            if self.enable_logging:
                print(f"Semantic analysis error: {e}")
        
        return GuardrailResult(passed=True, reason="Semantic analysis passed", action="allow")
    
    # ==================== Layer 5: Risk Scoring ====================
    
    def _calculate_risk_score(self, text: str, profile: UserRiskProfile,
                             conversation_history: Optional[List[Dict]]) -> float:
        """Calculate risk score for user/message (0.0 = safe, 1.0 = high risk)"""
        risk_factors = []
        
        # Factor 1: User history (0-0.3)
        history_risk = min(profile.violation_count * 0.1, 0.3)
        risk_factors.append(history_risk)
        
        # Factor 2: Message complexity (0-0.2)
        complexity_risk = min(len(text) / 5000, 0.2)
        risk_factors.append(complexity_risk)
        
        # Factor 3: Suspicious patterns (0-0.3)
        pattern_risk = min(len(profile.suspicious_patterns) * 0.1, 0.3)
        risk_factors.append(pattern_risk)
        
        # Factor 4: Recent warnings (0-0.2)
        recent_warnings = [w for w in profile.warnings 
                          if datetime.fromisoformat(w["timestamp"]) > datetime.now() - timedelta(hours=1)]
        warning_risk = min(len(recent_warnings) * 0.1, 0.2)
        risk_factors.append(warning_risk)
        
        return min(sum(risk_factors), 1.0)
    
    def _risk_score_to_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score < 0.2:
            return RiskLevel.SAFE
        elif score < 0.4:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    # ==================== Output Validation ====================
    
    def _layer1_output_safety(self, bot_response: str) -> GuardrailResult:
        """Fast output safety checks"""
        
        # Check for system leakage
        system_keywords = [
            "system:", "assistant:", "you are a", "bạn là một ai",
            "api_key", "token", "password", "mật khẩu"
        ]
        
        response_lower = bot_response.lower()
        if any(kw in response_lower for kw in system_keywords):
            return GuardrailResult(
                passed=False,
                reason="System information leakage detected",
                action="block",
                modified_content="Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.",
                severity="critical",
                risk_level=RiskLevel.CRITICAL
            )
        
        # Check response length
        if len(bot_response.strip()) < 10:
            return GuardrailResult(
                passed=False,
                reason="Response too short (likely error)",
                action="block",
                modified_content="Xin lỗi, tôi cần suy nghĩ lại. Vui lòng thử lại.",
                severity="warning",
                risk_level=RiskLevel.LOW
            )
        
        return GuardrailResult(passed=True, reason="Output safety checks passed", action="allow")
    
    def _layer2_medical_compliance(self, bot_response: str, user_input: str) -> GuardrailResult:
        """Medical ethics and compliance validation"""
        
        response_lower = bot_response.lower()
        
        # Check for definitive diagnosis (forbidden)
        diagnosis_patterns = [
            r'bạn (bị|có) bệnh',
            r'đây là bệnh',
            r'chẩn đoán (là|của bạn)',
            r'you (have|got) (a )?(disease|condition)',
            r'(my )?diagnosis is'
        ]
        
        for pattern in diagnosis_patterns:
            if re.search(pattern, response_lower):
                return GuardrailResult(
                    passed=False,
                    reason="Bot providing medical diagnosis (forbidden)",
                    action="block",
                    modified_content=(
                        "Tôi không thể đưa ra chẩn đoán y tế. "
                        "Vui lòng đặt lịch khám với bác sĩ để được tư vấn chính xác."
                    ),
                    severity="critical",
                    risk_level=RiskLevel.CRITICAL,
                    compliance_violations=["MEDICAL_DIAGNOSIS"]
                )
        
        # Check for medication prescription (forbidden)
        prescription_patterns = [
            r'(uống|dùng|sử dụng) thuốc',
            r'liều lượng',
            r'kê đơn',
            r'take (this )?(medicine|drug|medication)',
            r'dosage',
            r'prescription'
        ]
        
        for pattern in prescription_patterns:
            if re.search(pattern, response_lower):
                # Check if it's general information vs. specific prescription
                if any(safe_phrase in response_lower for safe_phrase in ["bác sĩ sẽ", "doctor will", "tham khảo bác sĩ"]):
                    continue  # Safe context
                
                return GuardrailResult(
                    passed=False,
                    reason="Bot prescribing medication (forbidden)",
                    action="block",
                    modified_content=(
                        "Tôi không thể kê đơn thuốc. "
                        "Chỉ bác sĩ có thẩm quyền kê đơn sau khi khám."
                    ),
                    severity="critical",
                    risk_level=RiskLevel.CRITICAL,
                    compliance_violations=["MEDICATION_PRESCRIPTION"]
                )
        
        return GuardrailResult(passed=True, reason="Medical compliance passed", action="allow")
    
    def _assess_conversation_quality(self, bot_response: str, user_input: str,
                                    conversation_history: Optional[List[Dict]]) -> ConversationQualityMetrics:
        """Assess conversation quality using AI"""
        
        if not self.thorough_model:
            return ConversationQualityMetrics()
        
        try:
            context = ""
            if conversation_history:
                recent = conversation_history[-3:]
                context = "\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in recent])
            
            prompt = f"""Evaluate this chatbot response quality in a medical clinic context.

Context: {context}
User: {user_input}
Bot: {bot_response}

Rate each dimension (0.0-1.0):
1. Coherence: Is response logical and well-structured?
2. Helpfulness: Does it address user's need?
3. Safety: Is it medically safe and appropriate?
4. Professionalism: Is tone professional and empathetic?

Respond with JSON only:
{{
  "coherence": 0.0-1.0,
  "helpfulness": 0.0-1.0,
  "safety": 0.0-1.0,
  "professionalism": 0.0-1.0
}}
"""
            
            response = self.thorough_model.generate_content(prompt)
            result_text = response.text.strip()
            
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group(0))
                
                metrics = ConversationQualityMetrics(
                    coherence_score=scores.get("coherence", 0.5),
                    helpfulness_score=scores.get("helpfulness", 0.5),
                    safety_score=scores.get("safety", 0.5),
                    professionalism_score=scores.get("professionalism", 0.5)
                )
                
                # Calculate overall score
                metrics.overall_score = (
                    metrics.coherence_score * 0.2 +
                    metrics.helpfulness_score * 0.3 +
                    metrics.safety_score * 0.3 +
                    metrics.professionalism_score * 0.2
                )
                
                return metrics
            
        except Exception as e:
            if self.enable_logging:
                print(f"Quality assessment error: {e}")
        
        return ConversationQualityMetrics()
    
    # ==================== Logging & Monitoring ====================
    
    def _log_incident(self, user_id: str, incident_type: str, result: GuardrailResult):
        """Log security/compliance incident"""
        incident = {
            "timestamp": datetime.now().isoformat(),
            "user_id": self._hash_user_id(user_id),  # Privacy
            "incident_type": incident_type,
            "severity": result.severity,
            "risk_level": result.risk_level.value,
            "reason": result.reason,
            "compliance_violations": result.compliance_violations
        }
        
        self.incident_log.append(incident)
        
        if self.enable_logging:
            print(f"🚨 INCIDENT: {incident_type} - {result.reason}")
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy in logs"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            "type": "advanced",
            "total_checks": self.stats["total_checks"],
            "risk_levels": dict(self.stats["risk_levels"]),
            "compliance_violations": dict(self.stats["compliance_violations"]),
            "adversarial_attempts": self.stats["adversarial_attempts"],
            "pii_detected": self.stats["pii_detected"],
            "active_users": len(self.user_profiles),
            "high_risk_users": sum(1 for p in self.user_profiles.values() if p.risk_score > 0.6),
            "recent_incidents": len(self.incident_log)
        }
    
    def get_user_risk_profile(self, user_id: str) -> Optional[UserRiskProfile]:
        """Get risk profile for a specific user"""
        return self.user_profiles.get(user_id)
    
    def export_compliance_report(self, start_date: Optional[datetime] = None) -> Dict:
        """Export compliance report for audit"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        
        relevant_incidents = [
            incident for incident in self.incident_log
            if datetime.fromisoformat(incident["timestamp"]) >= start_date
        ]
        
        return {
            "report_date": datetime.now().isoformat(),
            "period_start": start_date.isoformat(),
            "total_incidents": len(relevant_incidents),
            "incidents_by_type": self._group_by(relevant_incidents, "incident_type"),
            "incidents_by_severity": self._group_by(relevant_incidents, "severity"),
            "compliance_violations": self._count_violations(relevant_incidents),
            "summary": {
                "critical_incidents": len([i for i in relevant_incidents if i["severity"] == "critical"]),
                "high_risk_events": len([i for i in relevant_incidents if i["risk_level"] == "high"])
            }
        }
    
    def _group_by(self, incidents: List[Dict], key: str) -> Dict[str, int]:
        """Group incidents by a key"""
        result = defaultdict(int)
        for incident in incidents:
            result[incident.get(key, "unknown")] += 1
        return dict(result)
    
    def _count_violations(self, incidents: List[Dict]) -> Dict[str, int]:
        """Count compliance violations"""
        result = defaultdict(int)
        for incident in incidents:
            for violation in incident.get("compliance_violations", []):
                result[violation] += 1
        return dict(result)


# Example usage
if __name__ == "__main__":
    guardrail = AdvancedGuardrail()
    
    print("Advanced Guardrail System initialized")
    print(f"Features: Multi-layer validation, Compliance checking, Risk profiling")
    
    test_case = "Tôi bị đau đầu và sốt, có phải bệnh gì nghiêm trọng không?"
    result = guardrail.check_input(test_case, user_id="test_user_123")
    
    print(f"\n{'='*60}")
    print(f"Test input: {test_case}")
    print(f"Result: {result}")
    print(f"\nStats: {guardrail.get_stats()}")
