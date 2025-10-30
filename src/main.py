"""FastAPI server for Medical Clinic Chatbot"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from datetime import datetime
import os

from configs.config import CLINIC_CONFIG, MODEL_NAME
from agents.medical_diagnostic_graph import MedicalDiagnosticGraph

from routes import faq_router, todo_router
# Initialize FastAPI app
app = FastAPI(
    title="Medical Clinic Chatbot API",
    description="REST API for AI-powered medical clinic assistant",
    version="1.0.0",
)
app.include_router(faq_router)
app.include_router(todo_router)
# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")




# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Conversation session ID")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Bot's response")
    session_id: str = Field(..., description="Conversation session ID")
    timestamp: str = Field(..., description="Response timestamp")


class ImageChatRequest(BaseModel):
    """Request model for image chat endpoint"""
    message: str = Field(..., description="User's text message/symptoms")
    image: str = Field(..., description="Base64 encoded image data (with or without data URI prefix)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")


class HistoryResponse(BaseModel):
    """Response model for conversation history"""
    session_id: str
    messages: List[Dict[str, str]]


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    model: str
    clinic: str


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - Serve frontend or API info"""
    # Check if frontend exists
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    else:
        return {
            "message": "Welcome to Medical Clinic Chatbot API",
            "docs": "/docs",
            "health": "/health",
            "chat": "/chat (POST)",
        }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="gemini-2.0-flash-lite",
        clinic=CLINIC_CONFIG["name"]
    )


@app.post("/ma/chat", response_model=ChatResponse)
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


@app.post("/ma/chat/image", tags=["Chat"])
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




@app.get("/clinic/info")
async def clinic_info():
    """Get general clinic information"""
    return {
        "name": CLINIC_CONFIG["name"],
        "hours": CLINIC_CONFIG["hours"],
        "phone": CLINIC_CONFIG["phone"],
        "address": CLINIC_CONFIG["address"],
        "providers": CLINIC_CONFIG["providers"],
    }

