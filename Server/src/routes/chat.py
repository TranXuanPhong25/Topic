from . import chat_router
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from src.middleware.guardrails import (
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

diagnostic_graph = MedicalDiagnosticGraph()

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

        if _is_simple_greeting(request.message):
            return {
                "session_id": session_id,
                "response": "Hello! I'm your virtual assistant. How can I help you today (appointments, symptoms, FAQs)?",
                "timestamp": datetime.now().isoformat()
            }
        
        if GUARDRAILS_ENABLED:
            # Use lightweight dedicated model for fast guardrail checking
            should_block, action = check_guardrail_simple(request.message)
            
            if should_block and action is not None:
                # Log guardrail decision for debugging/monitoring
                return {
                    "session_id": session_id,
                    "response": "Your message was refused due to security policies.",
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
        return {
            "session_id": session_id,
            "response": final_response,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\nError in multi-agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


@chat_router.post("/ma/chat/image", tags=["Chat"])
async def ma_chat_with_image(request: ImageChatRequest):
    try:
        # Validate image data
        if not request.image:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        session_id = request.session_id or str(uuid.uuid4())

        if GUARDRAILS_ENABLED:
            should_block, action = check_guardrail_simple(
                request.message or ""
            )
            
            if should_block and action is not None:
                return {
                    "session_id": session_id,
                    "response": "Your message was refused due to security policies.",
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
            print(f"Image chat history: {len(chat_history)} messages")
        
        result = await diagnostic_graph.analyze(request.message, request.image, chat_history=chat_history)

        final_response = result['final_response']

        return {
            "session_id": session_id,
            "response": final_response,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\nError in multi-agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


@chat_router.post("/ma/chat/stream", tags=["Chat"])
async def ma_chat_stream(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_generator():
        try:
            # Fast guardrail pre-check before starting streaming analysis
            if GUARDRAILS_ENABLED:
                should_block, action = check_guardrail_simple( request.message)
                
                if should_block and action is not None:
                    event_data = json.dumps({
                        "type": "final",
                        "session_id": session_id,
                        "content": "Your message was refused due to security policies.",
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
            print(f"Stream error: {str(e)}")
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

