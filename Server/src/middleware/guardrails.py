from __future__ import annotations
from typing import Tuple, Optional, Dict, List
import json
import base64

# Deprecated regex-based filters kept only for backward compatibility if needed.
NON_MEDICAL_KEYWORDS: List[str] = []
PRESCRIPTION_KEYWORDS: List[str] = []
SELF_HARM_KEYWORDS: List[str] = []
EMERGENCY_KEYWORDS: List[str] = []


def classify_intent(text: str) -> Optional[str]:
    """Legacy stub kept for compatibility; main classification is now LLM-based."""
    return None


def detect_prescription_request(text: str) -> bool:
    return False


def detect_self_harm(text: str) -> bool:
    return False


def detect_emergency(text: str) -> bool:
    return False


_VI_CHARS = set("ăâêôơưđáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
_VI_WORDS = {"tôi", "muốn", "không", "có", "bác", "sĩ", "thuốc", "đau", "ngực", "khó", "thở", "vẫn", "tự", "sát"}

def detect_language(text: str) -> str:
    t = text.lower()
    if any(ch in _VI_CHARS for ch in t) or any(w in t for w in _VI_WORDS):
        return 'vi'
    return 'en'


def build_simple_guardrail_prompt(text: str, has_image: bool = False) -> str:
    """Simplified, fast prompt for guardrail pre-check before agent processing.
    
    Optimized for speed and token efficiency. Returns only JSON boolean.
    
    Args:
        text: User message to check
        has_image: Whether request includes a medical image (X-ray, skin photo, etc.)
    """
    image_context = ""
    if has_image:
        image_context = (
            "\n**IMPORTANT CONTEXT**: This message is accompanied by a MEDICAL IMAGE (X-ray, photo of symptoms, medical document, etc.).\n"
            "- ALWAYS ALLOW messages about medical images, symptoms shown in images, or asking for image analysis\n"
            "- Examples: 'đây là ảnh bệnh của tôi', 'check this rash', 'X-ray results', 'skin condition photo'\n\n"
        )
    
    return (
        "You are a medical chatbot content filter. Reply ONLY with JSON, no explanation.\n\n"
        f"{image_context}"
        "Check if this message is SAFE for a medical assistant:\n"
        "- BLOCK if: sports, games, crypto/finance, politics, entertainment, tech/coding, weather, travel, cooking, or any NON-HEALTH topic\n"
        "- BLOCK if: violence, self-harm, graphic content, hate speech, sexual content\n"
        "- BLOCK if: requests for drug prescriptions, dosages, supplements, treatment schedules\n\n"
        "- ALLOW if: symptoms, health concerns, clinic appointments, general medical questions, medical images\n\n"
        "Examples (Vietnamese/English):\n"
        "✗ BLOCK: 'đá bóng', 'bitcoin', 'chính trị', 'phim', 'python code'\n"
        "✓ ALLOW: 'đau đầu', 'khó thở', 'đặt lịch khám', 'fever', 'book appointment', 'ảnh bệnh', 'X-ray'\n\n"
        f"Message: {text}\n\n"
        "Return JSON: {\"should_block\": true/false}"
    )

def build_classifier_prompt(text: str) -> str:
    """Detailed prompt for LLM to classify safety-related aspects of text.
    
    Used for comprehensive analysis when simple check needs breakdown.

    The model MUST return ONLY JSON with this schema:
    {
      "is_violent_or_sensitive": bool,
      "is_prescription_or_dosage": bool,
      "is_supplement": bool,
      "is_non_medical_topic": bool
    }
    """
    return (
        "You are a safety classifier for a medical clinic chatbot.\n"
        "You MUST return ONLY valid JSON, no explanations.\n\n"
        "Tasks:\n"
        "1. Detect if the text contains:\n"
        "   - Violence or graphic/sensitive content (blood, self-harm details, sexual content, hate).\n"
        "   - Mentions of drugs, medications, dosages, or treatment schedules.\n"
        "   - Mentions of supplements, vitamins, or functional foods.\n"
        "   - Topics that are clearly NOT related to health or medicine.\n\n"
        "2. For NON-MEDICAL topics, consider these categories:\n"
        "   - Sports (football, soccer, basketball, tennis, swimming, esports, gaming, etc.)\n"
        "   - Finance/Crypto (bitcoin, stocks, trading, lottery, betting, investments, etc.)\n"
        "   - Politics (elections, government, political parties, etc.)\n"
        "   - Entertainment (movies, music, celebrities, showbiz, etc.)\n"
        "   - Technology/Coding (programming, software bugs, hacking, etc.)\n"
        "   - General topics (weather, travel, cooking recipes, etc.)\n"
        "   BE STRICT: If the topic is not clearly about health, symptoms, medical conditions,\n"
        "   appointments, or clinic services, mark it as non-medical.\n\n"
        "3. The text may be in English or Vietnamese. Understand both.\n"
        "   Vietnamese examples:\n"
        "   - Medical: 'đau đầu', 'khó thở', 'bác sĩ', 'thuốc', 'khám bệnh', 'triệu chứng'\n"
        "   - Non-medical: 'đá bóng', 'chơi game', 'bitcoin', 'phim ảnh', 'chính trị', 'nấu ăn'\n\n"
        "Return JSON with this exact schema:\n"
        "{\n"
        "  \"is_violent_or_sensitive\": true/false,\n"
        "  \"is_prescription_or_dosage\": true/false,\n"
        "  \"is_supplement\": true/false,\n"
        "  \"is_non_medical_topic\": true/false\n"
        "}\n\n"
        f"Text to classify:\n{text}"
    )


def check_image_medical_relevance(vision_model, image_base64: str) -> Tuple[bool, Optional[str]]:
    """Check if image is medically relevant using vision model.
    
    Args:
        vision_model: Vision-capable model (Gemini with image support)
        image_base64: Base64 encoded image data
    
    Returns:
        (is_medical: bool, reason: Optional[str])
        - is_medical: True if image is medically relevant
        - reason: Explanation if not medical
    """
    try:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        # Decode base64 image
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
        
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt = (
            "You are a medical image classifier. Analyze this image and determine if it's medically relevant.\n\n"
            "MEDICAL images include:\n"
            "- Medical scans (X-ray, CT, MRI, ultrasound)\n"
            "- Skin conditions, rashes, wounds, injuries\n"
            "- Body parts showing symptoms (swelling, discoloration, abnormalities)\n"
            "- Medical documents (prescriptions, lab results, medical reports)\n"
            "- Medical equipment or procedures\n\n"
            "NON-MEDICAL images include:\n"
            "- Landscapes, buildings, scenery\n"
            "- Food, recipes, cooking\n"
            "- Sports, games, entertainment\n"
            "- Animals, pets (unless showing medical issue)\n"
            "- Screenshots of non-medical content\n"
            "- General photos unrelated to health\n\n"
            "Reply ONLY with JSON: {\"is_medical\": true/false, \"reason\": \"brief explanation\"}"
        )
        
        # Use Gemini vision API directly
        from src.configs.agent_config import GOOGLE_API_KEY
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content([prompt, image])
        raw = response.text.strip()
        
        # Parse JSON
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        
        data = json.loads(raw)
        is_medical = bool(data.get("is_medical", True))  # Default to True (fail open)
        reason = data.get("reason", "")
        
        if not is_medical:
            print(f"🛡 Image rejected as non-medical: {reason}")
            return False, reason
        
        return True, None
        
    except Exception as e:
        print(f"⚠️ Image classification error: {e} - Allowing through (fail open)")
        import traceback
        traceback.print_exc()
        # Fail open - if we can't classify, allow the image
        return True, None


def check_guardrail_simple(model, text: str, has_image: bool = False, image_data: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Fast guardrail check using simple LLM prompt.
    
    Args:
        model: LangChain ChatGoogleGenerativeAI instance
        text: User input to check
        has_image: Whether the request includes an image
        image_data: Base64 image data for content validation
    
    Returns:
        (should_block: bool, reason: Optional[str])
        - should_block: True if message should be blocked
        - reason: Generic reason category if blocked (for refusal message)
    """
    try:
        # If image provided, validate it's medically relevant
        if has_image and image_data:
            is_medical, img_reason = check_image_medical_relevance(model, image_data)
            if not is_medical:
                print(f"🛡 Guardrail blocked non-medical image: {img_reason}")
                return True, "non_medical"
        
        # Check text content
        prompt = build_simple_guardrail_prompt(text, has_image)
        
        # Use LangChain's invoke() method
        from langchain_core.messages import HumanMessage
        resp = model.invoke([HumanMessage(content=prompt)])
        raw = resp.content if hasattr(resp, 'content') else str(resp)
        raw = raw.strip()
        
        # Handle markdown code blocks
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        
        data = json.loads(raw)
        should_block = bool(data.get("should_block", False))
        
        # If blocked, return generic non_medical reason (avoid extra API call)
        # This saves 1 API call per blocked request
        if should_block:
            return True, "non_medical"
        
        return False, None
        
    except Exception as e:
        # On error, allow message through (fail open for availability)
        print(f"⚠️ Guardrail check error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def classify_content_llm(model, text: str) -> Dict[str, bool]:
    """Use an LLM to classify text for safety guardrails with detailed breakdown.
    
    Args:
        model: LangChain ChatGoogleGenerativeAI instance
        text: Content to classify

    Returns dict with keys used by higher-level guardrail logic.
    On error, returns all False (treat as safe, caller can decide fallback).
    """
    try:
        prompt = build_classifier_prompt(text)
        
        # Use LangChain's invoke() method
        from langchain_core.messages import HumanMessage
        resp = model.invoke([HumanMessage(content=prompt)])
        raw = resp.content if hasattr(resp, 'content') else str(resp)
        raw = raw.strip()
        
        # Try to extract JSON directly
        # Handle potential markdown code blocks if the model outputs them
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        
        data = json.loads(raw)
        return {
            "is_violent_or_sensitive": bool(data.get("is_violent_or_sensitive", False)),
            "is_prescription_or_dosage": bool(data.get("is_prescription_or_dosage", False)),
            "is_supplement": bool(data.get("is_supplement", False)),
            "is_non_medical_topic": bool(data.get("is_non_medical_topic", False)),
        }
    except Exception as e:
        print(f"⚠️ Classification error: {e}")
        return {
            "is_violent_or_sensitive": False,
            "is_prescription_or_dosage": False,
            "is_supplement": False,
            "is_non_medical_topic": False,
        }


def apply_guardrails(text: str) -> Tuple[bool, Optional[str], str, Dict[str, any]]:
    """Legacy input guardrail: now only returns original text without changes.

    New code should prefer `classify_content_llm` + action mapping.
    """
    meta: Dict[str, any] = {}
    action: Optional[str] = None
    return True, action, text, meta


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
    
    Args:
        model: LangChain ChatGoogleGenerativeAI instance
        action: Type of refusal (self_harm, prescription, non_medical, etc.)
        text: Original user message
        lang: Language code (vi/en)
    """
    try:
        prompt = build_refusal_prompt(action, text=text, lang=lang)
        
        # Use LangChain's invoke() method
        from langchain_core.messages import HumanMessage
        resp = model.invoke([HumanMessage(content=prompt)])
        msg = resp.content if hasattr(resp, 'content') else str(resp)
        # Basic sanitation: trim and fallback if empty
        msg = msg.strip()
        if msg:
            return msg
    except Exception as e:
        print(f"⚠️ Refusal generation error: {e}")
    
    # Fallback if LLM fails
    return refusal_message(action, text, lang)


def refusal_message(action: str, text: Optional[str] = None, lang: Optional[str] = None) -> str:
    """Simple, static fallback refusal message.

    Kept for backwards compatibility with existing code that imports
    `refusal_message`. For richer, localized responses, prefer
    `refusal_message_llm` which uses the LLM and `build_refusal_prompt`.
    """
    chosen_lang = lang or (detect_language(text or "") if text is not None else 'en')

    if action == 'self_harm':
        if chosen_lang == 'vi':
            return (
                "Nếu bạn đang nghĩ đến việc tự hại hoặc tự tử, hãy tìm sự giúp đỡ ngay lập tức. "
                "Hãy liên hệ dịch vụ khẩn cấp hoặc một chuyên gia đáng tin cậy. Bạn rất quan trọng."
            )
        return (
            "If you're thinking about self-harm or suicide, please seek immediate help. "
            "Contact local emergency services or a trusted professional right now. You matter."
        )

    if action == 'emergency':
        if chosen_lang == 'vi':
            return (
                "Mô tả của bạn có thể cho thấy tình huống khẩn cấp. "
                "Hãy tìm trợ giúp y tế ngay hoặc gọi dịch vụ khẩn cấp."
            )
        return (
            "Your description may indicate a medical emergency. "
            "Please seek immediate medical attention or call emergency services."
        )

    if action == 'prescription':
        if chosen_lang == 'vi':
            return (
                "Mình không thể kê đơn hoặc đưa ra liều lượng thuốc cụ thể. "
                "Vui lòng trao đổi với bác sĩ hoặc nhân viên y tế được cấp phép để được hướng dẫn về thuốc."
            )
        return (
            "I can't provide prescriptions, specific medication dosages, or treatment schedules. "
            "Please consult a licensed healthcare professional for medication guidance."
        )

    if action == 'non_medical':
        if chosen_lang == 'vi':
            return (
                "Mình chỉ hỗ trợ các câu hỏi liên quan đến y tế và sức khỏe. "
                "Bạn có thể hỏi về triệu chứng, hướng dẫn chăm sóc sức khỏe, hoặc dịch vụ của phòng khám."
            )
        return (
            "I can only help with medical or health-related questions. "
            "Please ask about symptoms, general health guidance, or clinic services."
        )

    # Default generic fallback
    return "I'm unable to process this request."


__all__ = [
    'apply_guardrails', 'refusal_message', 'build_refusal_prompt', 'refusal_message_llm',
    'build_classifier_prompt', 'classify_content_llm', 'check_guardrail_simple',
    'detect_emergency', 'detect_self_harm', 'detect_prescription_request', 'classify_intent', 'detect_language'
]