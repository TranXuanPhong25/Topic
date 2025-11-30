from . import chat_router
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.middleware.guardrails import apply_guardrails, refusal_message
import uuid
from datetime import datetime
from fastapi import HTTPException
from src.models.chat import ChatRequest, ImageChatRequest, ChatResponse

# Reuse a single graph instance to avoid re-initializing models every request
# (Frequent reinitialization causes multiple concurrent Gemini calls and rate limits)
diagnostic_graph = MedicalDiagnosticGraph()

# Optional: draw once at startup (comment out if noisy in logs)
try:
    print(diagnostic_graph.graph.get_graph().draw_ascii())
except Exception:
    pass




GREETING_KEYWORDS = {"hi", "hello", "hey", "xin chào", "chào", "good morning", "good afternoon"}

def _is_simple_greeting(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    # Single word or very short greeting without medical content
    if len(t.split()) <= 3 and any(k in t for k in GREETING_KEYWORDS):
        return True
    return False

@chat_router.post("/ma/chat", response_model=ChatResponse)
async def ma_chat(request: ChatRequest):
    """
    Main chat endpoint - send a message and get a response.
    
    Args:
        request: ChatRequest with message and optional session_id
        
    Returns:
        ChatResponse with bot's reply, session_id, and timestamp
    """
    try:

        session_id = request.session_id or str(uuid.uuid4())

        # Fast path: simple greeting -> lightweight response, avoid full graph
        if _is_simple_greeting(request.message):
            return {
                "session_id": session_id,
                "response": "Hello! I'm your virtual assistant. How can I help you today (appointments, symptoms, FAQs)?",
                "analysis": None,
                "diagnosis": None,
                "risk_assessment": None,
                "investigation_plan": None,
                "recommendation": None,
                "timestamp": datetime.now().isoformat()
            }

        # Guardrails: sanitize & possibly short-circuit
        safe, action, sanitized, meta = apply_guardrails(request.message)
        if not safe:
            session_id = request.session_id or str(uuid.uuid4())
            return {
                "session_id": session_id,
                "response": refusal_message(action, text=request.message),
                "analysis": None,
                "diagnosis": None,
                "risk_assessment": None,
                "investigation_plan": None,
                "recommendation": None,
                "timestamp": datetime.now().isoformat()
            }

        # Run multi-agent diagnostic pipeline (single shared instance) with sanitized input
        result = diagnostic_graph.analyze(user_input=sanitized, metadata={"guardrails": meta})
    
        return {
            "session_id": session_id,
            "response": result['final_response'],
            "analysis": result.get("detailed_analysis"),
            "diagnosis": result.get("diagnosis"),
            "risk_assessment": result.get("risk_assessment"),
            "investigation_plan": result.get("investigation_plan"),
            "recommendation": result.get("recommendation"),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error in multi-agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


@chat_router.post("/ma/chat/image", tags=["Chat"])
def ma_chat_with_image(request: ImageChatRequest):
    """
    Multi-agent chat with image analysis.
    
    Uses the complete multi-agent workflow:
    Vision Agent → Symptom Matcher → Risk Assessor → Recommender
    
    Returns comprehensive medical image analysis.
    """
    try:
        # Validate image data
        if not request.image:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        session_id = request.session_id or str(uuid.uuid4())

        safe, action, sanitized, meta = apply_guardrails(request.message)
        if not safe:
            session_id = request.session_id or str(uuid.uuid4())
            return {
                "session_id": session_id,
                "response": refusal_message(action, text=request.message),
                "analysis": None,
                "diagnosis": None,
                "risk_assessment": None,
                "investigation_plan": None,
                "recommendation": None,
                "timestamp": datetime.now().isoformat()
            }
        result = diagnostic_graph.analyze(sanitized, request.image, metadata={"guardrails": meta})
        
        return {
            "session_id": session_id,
            "response": result['final_response'],
            "analysis": result.get("detailed_analysis"),
            "diagnosis": result.get("diagnosis"),
            "risk_assessment": result.get("risk_assessment"),
            "investigation_plan": result.get("investigation_plan"),
            "recommendation": result.get("recommendation"),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error in multi-agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )



