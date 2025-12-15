from . import chat_router
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.middleware.guardrails import (
    apply_guardrails,
    refusal_message,
    refusal_message_llm,
    classify_content_llm,
    check_guardrail_simple,
)
from src.configs.config import GUARDRAILS_ENABLED, GUARDRAILS_CHECK_OUTPUT
import uuid
import json
import asyncio
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
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
                "timestamp": datetime.now().isoformat()
            }
        
        # Fast guardrail pre-check BEFORE entering agent graph (saves resources)
        if GUARDRAILS_ENABLED:
            # Use lightweight model for fast guardrail checking
            from src.agents.conversation_agent.config import get_conversation_model
            model = get_conversation_model()
            should_block, action = check_guardrail_simple(model, request.message)
            
            if should_block and action is not None:
                # Log guardrail decision for debugging/monitoring
                print(f"🛡 Guardrail blocked input. Action={action}, text={request.message!r}")
                msg = refusal_message_llm(model, action, text=request.message)
                return {
                    "session_id": session_id,
                    "response": msg,
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
        
        # Run multi-agent diagnostic pipeline (single shared instance)
        result = await diagnostic_graph.analyze(user_input=request.message, chat_history=chat_history)

        final_response = result['final_response']

        # Optional output guardrails: rewrite unsafe responses
        if GUARDRAILS_ENABLED and GUARDRAILS_CHECK_OUTPUT and diagnostic_graph.gemini_model is not None:
            cls_out = classify_content_llm(diagnostic_graph.gemini_model, final_response)
            if any(cls_out.values()):
                # If output unsafe, ask LLM to rewrite a safe version using refusal_message_llm-style prompt
                # Reuse prescription / non_medical for mapping, and treat violent/sensitive as self_harm-style crisis guard.
                if cls_out.get("is_violent_or_sensitive"):
                    action_out = "self_harm"
                elif cls_out.get("is_prescription_or_dosage") or cls_out.get("is_supplement"):
                    action_out = "prescription"
                elif cls_out.get("is_non_medical_topic"):
                    action_out = "non_medical"
                else:
                    action_out = None

                if action_out is not None:
                    safe_msg = refusal_message_llm(diagnostic_graph.gemini_model, action_out, text=final_response)
                    final_response = safe_msg
    
        return {
            "session_id": session_id,
            "response": final_response,
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
async def ma_chat_with_image(request: ImageChatRequest):
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

        # Fast guardrail pre-check for image chat
        if GUARDRAILS_ENABLED:
            from src.agents.conversation_agent.config import get_conversation_model
            model = get_conversation_model()
            should_block, action = check_guardrail_simple(model, request.message or "")
            
            if should_block and action is not None:
                print(f"🛡 Guardrail blocked image-chat input. Action={action}, text={request.message!r}")
                msg = refusal_message_llm(model, action, text=request.message)
                return {
                    "session_id": session_id,
                    "response": msg,
                    "timestamp": datetime.now().isoformat()
                }
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
        
        result = await diagnostic_graph.analyze(request.message, request.image, chat_history=chat_history)

        final_response = result['final_response']

        if GUARDRAILS_ENABLED and GUARDRAILS_CHECK_OUTPUT and diagnostic_graph.gemini_model is not None:
            cls_out = classify_content_llm(diagnostic_graph.gemini_model, final_response)
            if any(cls_out.values()):
                if cls_out.get("is_violent_or_sensitive"):
                    action_out = "self_harm"
                elif cls_out.get("is_prescription_or_dosage") or cls_out.get("is_supplement"):
                    action_out = "prescription"
                elif cls_out.get("is_non_medical_topic"):
                    action_out = "non_medical"
                else:
                    action_out = None

                if action_out is not None:
                    safe_msg = refusal_message_llm(diagnostic_graph.gemini_model, action_out, text=final_response)
                    final_response = safe_msg
        
        return {
            "session_id": session_id,
            "response": final_response,
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


@chat_router.post("/ma/chat/stream", tags=["Chat"])
async def ma_chat_stream(request: ChatRequest):
    """
    Streaming multi-agent chat endpoint using Server-Sent Events (SSE).
    
    Sends intermediate messages (e.g., "checking availability...") as they happen,
    then sends the final response.
    
    Event types:
    - intermediate: Partial response while processing (e.g., tool acknowledgment)
    - final: Complete response
    - error: Error occurred
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_generator():
        try:
            # Fast guardrail pre-check before starting streaming analysis
            if GUARDRAILS_ENABLED:
                from src.agents.conversation_agent.config import get_conversation_model
                model = get_conversation_model()
                should_block, action = check_guardrail_simple(model, request.message)
                
                if should_block and action is not None:
                    print(f"🛡 Guardrail blocked streaming input. Action={action}, text={request.message!r}")
                    msg = refusal_message_llm(model, action, text=request.message)
                    event_data = json.dumps({
                        "type": "final",
                        "session_id": session_id,
                        "content": msg,
                        "timestamp": datetime.now().isoformat(),
                    })
                    yield f"data: {event_data}\n\n"
                    return
            # Convert chat_history
            chat_history = None
            if request.chat_history:
                chat_history = [
                    {
                        "role": msg.role,
                        "parts": [{"text": part.text} for part in msg.parts]
                    }
                    for msg in request.chat_history[-20:]
                ]
            
            # Run analysis with streaming callback
            result = await diagnostic_graph.analyze_stream(
                user_input=request.message,
                chat_history=chat_history,
                on_intermediate=lambda msg: None  # Callback will be handled via queue
            )
            
            # Check if we have intermediate messages
            intermediate_messages = result.get('intermediate_messages', [])
            for msg in intermediate_messages:
                event_data = json.dumps({
                    "type": "intermediate",
                    "content": msg,
                    "timestamp": datetime.now().isoformat()
                })
                yield f"data: {event_data}\n\n"
                await asyncio.sleep(0.01)  # Small delay to ensure delivery
            
            # Send final response
            final_data = json.dumps({
                "type": "final",
                "session_id": session_id,
                "content": result['final_response'],
                "timestamp": datetime.now().isoformat()
            })
            yield f"data: {final_data}\n\n"
            
        except Exception as e:
            print(f"❌ Stream error: {str(e)}")
            import traceback
            traceback.print_exc()
            error_data = json.dumps({
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

