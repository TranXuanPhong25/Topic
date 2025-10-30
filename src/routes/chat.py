from . import chat_router
from agents.medical_diagnostic_graph import MedicalDiagnosticGraph
import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import HTTPException
from models.chat import ChatRequest, ImageChatRequest, ChatResponse



# API Endpoints
graph = MedicalDiagnosticGraph()._build_graph()
print(graph.get_graph().draw_ascii())




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

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize multi-agent system
        agent_graph = MedicalDiagnosticGraph()

        # Run analysis
        result = agent_graph.analyze(user_input=request.message)
    
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
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize multi-agent system
        agent_graph = MedicalDiagnosticGraph()

        # Run analysis
        result = agent_graph.analyze(request.image, request.message)
    
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



