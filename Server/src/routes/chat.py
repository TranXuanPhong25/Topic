from . import chat_router
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
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
         # Convert chat_history to dict format if provided
        chat_history = None
        if request.chat_history:
            chat_history = [
                {
                    "role": msg.role,
                    "parts": [{"text": part.text} for part in msg.parts]
                }
                for msg in request.chat_history[-20:]
            ]
            print(f"📝 Chat history: {len(chat_history)} messages")
        
        # Run multi-agent diagnostic pipeline (single shared instance)
        result = diagnostic_graph.analyze(user_input=request.message, chat_history=chat_history)
    
        return {
            "session_id": session_id,
            "response": result['final_response'],
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
        chat_history = None
        if request.chat_history:
            chat_history = [
                {
                    "role": msg.role,
                    "parts": [{"text": part.text} for part in msg.parts]
                }
                for msg in request.chat_history[:-20]
            ]
            print(f"📝 Image chat history: {len(chat_history)} messages")
        
        result = diagnostic_graph.analyze(request.message, request.image, chat_history=chat_history)
        
        return {
            "session_id": session_id,
            "response": result['final_response'],
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



