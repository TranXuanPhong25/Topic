from . import chat_router
from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph
import uuid
from datetime import datetime
from fastapi import HTTPException
from src.models.chat import ChatRequest, ImageChatRequest, ChatResponse


graph = MedicalDiagnosticGraph()._build_graph()
print(graph.get_graph().draw_ascii())

@chat_router.post("/ma/chat", response_model=ChatResponse)
async def ma_chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Convert chat_history to dict format if provided
        chat_history = None
        if request.chat_history:
            chat_history = [
                {
                    "role": msg.role,
                    "parts": [{"text": part.text} for part in msg.parts]
                }
                for msg in request.chat_history
            ]
            print(f"📝 Chat history: {len(chat_history)} messages")
        
        # Initialize multi-agent system
        agent_graph = MedicalDiagnosticGraph()

        # Run analysis with chat history
        result = agent_graph.analyze(
            user_input=request.message,
            chat_history=chat_history
        )
    
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
    try:
        # Validate image data
        if not request.image:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Convert chat_history to dict format if provided
        chat_history = None
        if request.chat_history:
            chat_history = [
                {
                    "role": msg.role,
                    "parts": [{"text": part.text} for part in msg.parts]
                }
                for msg in request.chat_history
            ]
            print(f"📝 Image chat history: {len(chat_history)} messages")
        
        # Initialize multi-agent system
        agent_graph = MedicalDiagnosticGraph()

        # Run analysis with chat history
        result = agent_graph.analyze(
            user_input=request.message,
            image=request.image,
            chat_history=chat_history
        )
    
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



