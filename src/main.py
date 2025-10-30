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

from chatbot import ChatBot
from configs.config import CLINIC_CONFIG, MODEL_NAME
from agents.medical_diagnostic_graph import MedicalDiagnosticGraph
from todo_manager import todo_manager
from knowledge_base import knowledge_base
from database import get_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

# Initialize FastAPI app
app = FastAPI(
    title="Medical Clinic Chatbot API",
    description="REST API for AI-powered medical clinic assistant",
    version="1.0.0",
)

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

# Initialize chatbot (singleton)
chatbot = ChatBot()


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


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
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
        
        # Get response from chatbot
        response = chatbot.send_message(
            message=request.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/chat/image", tags=["Chat"])
async def chat_with_image(request: ImageChatRequest):
    """
    Chat endpoint with image upload for medical image analysis.
    
    This endpoint:
    1. Accepts a base64 encoded image and text symptoms
    2. Runs multi-agent analysis (vision + medical assessment)
    3. Returns detailed analysis with recommendations
    
    The image should be base64 encoded (with or without data URI prefix).
    Supports JPEG, PNG, WebP formats.
    Max recommended size: 5MB
    
    Args:
        request: ImageChatRequest with message, image, and optional session_id
        
    Returns:
        Complete analysis with visual description, medical assessment,
        risk level, and recommendations
    """
    try:
        # Validate image data
        if not request.image:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        # Check image size (rough check - base64 is ~1.37x original size)
        image_size_mb = len(request.image) / (1024 * 1024 * 1.37)
        if image_size_mb > 10:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail=f"Image too large ({image_size_mb:.1f}MB). Maximum size is 10MB."
            )
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message with image (async)
        result = await chatbot.handle_image_message(
            message=request.message,
            image_data=request.image,
            session_id=session_id
        )
        
        return {
            "session_id": session_id,
            "response": result["response"],
            "analysis": result.get("analysis"),
            "type": result.get("type"),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
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

@app.get("/chat/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Get conversation history for a session.
    
    Args:
        session_id: The conversation session ID
        
    Returns:
        HistoryResponse with all messages in the conversation
    """
    try:
        history = chatbot.get_chat_history(session_id)
        return HistoryResponse(
            session_id=session_id,
            messages=history
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session (start fresh conversation).
    
    Args:
        session_id: The conversation session ID to clear
        
    Returns:
        Success message
    """
    try:
        chatbot.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
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


# ==================== TODO ENDPOINTS ====================

class TodoCreateRequest(BaseModel):
    """Request model for creating a todo"""
    title: str = Field(..., description="Task title", min_length=1)
    description: str = Field(..., description="Task description", min_length=1)
    priority: Optional[str] = Field("medium", description="Priority: urgent/high/medium/low")
    category: Optional[str] = Field("other", description="Category: appointment/followup/callback/prescription/admin/other")
    assignee: Optional[str] = Field(None, description="Who should handle this task")
    due_hours: Optional[int] = Field(None, description="Hours from now when task is due")


class TodoUpdateRequest(BaseModel):
    """Request model for updating a todo"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None


@app.post("/todos")
async def create_todo(request: TodoCreateRequest):
    """Create a new todo task"""
    result = todo_manager.create_task(
        title=request.title,
        description=request.description,
        priority=request.priority or "medium",
        category=request.category or "other",
        assignee=request.assignee,
        due_hours=request.due_hours,
    )
    
    if result["success"]:
        return {"message": "Todo created", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create todo"))


@app.get("/todos")
async def get_todos(
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    include_completed: bool = False,
):
    """Get all todos with optional filters"""
    todos = todo_manager.get_tasks(
        assignee=assignee,
        status=status,
        priority=priority,
        category=category,
        include_completed=include_completed,
    )
    
    return {
        "message": "Todos retrieved",
        "count": len(todos),
        "todos": todos,
    }


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todo = todo_manager.get_task_by_id(todo_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    
    return {"message": "Todo retrieved", "todo": todo}


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, request: TodoUpdateRequest):
    """Update a todo task"""
    result = todo_manager.update_task(
        todo_id=todo_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        category=request.category,
        assignee=request.assignee,
        status=request.status,
    )
    
    if result["success"]:
        return {"message": "Todo updated", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update todo"))


@app.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int):
    """Mark a todo as completed"""
    result = todo_manager.complete_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo completed", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to complete todo"))


@app.post("/todos/{todo_id}/cancel")
async def cancel_todo(todo_id: int):
    """Mark a todo as cancelled"""
    result = todo_manager.cancel_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo cancelled", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to cancel todo"))


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo task"""
    result = todo_manager.delete_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo deleted"}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete todo"))


@app.get("/todos/overdue")
async def get_overdue_todos(assignee: Optional[str] = None):
    """Get all overdue todos"""
    todos = todo_manager.get_overdue_tasks(assignee=assignee)
    
    return {
        "message": "Overdue todos retrieved",
        "count": len(todos),
        "todos": todos,
    }


# ==================== KNOWLEDGE BASE ENDPOINTS ====================

@app.get("/faq/search")
async def search_faqs(q: str, limit: int = 5):
    """
    Search the FAQ knowledge base.
    
    Args:
        q: Search query
        limit: Maximum number of results (default: 5)
    """
    results = knowledge_base.search_faqs(q, limit=limit)
    
    return {
        "message": "Search completed",
        "query": q,
        "count": len(results),
        "results": results,
    }


@app.get("/faq/categories")
async def get_faq_categories():
    """Get all FAQ categories"""
    categories = knowledge_base.get_all_categories()
    
    return {
        "message": "Categories retrieved",
        "categories": categories,
    }


@app.get("/faq/category/{category}")
async def get_faqs_by_category(category: str):
    """Get all FAQs in a specific category"""
    faqs = knowledge_base.get_faq_by_category(category)
    
    if not faqs:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    return {
        "message": "FAQs retrieved",
        "category": category,
        "count": len(faqs),
        "faqs": faqs,
    }


@app.get("/faq/answer")
async def get_answer(q: str):
    """Get a direct answer to a question"""
    answer = knowledge_base.answer_question(q)
    
    if answer:
        return {
            "message": "Answer found",
            "query": q,
            "answer": answer,
        }
    else:
        return {
            "message": "No direct answer found",
            "query": q,
            "answer": "I don't have specific information about that. Please call us at (555) 123-4567 for assistance.",
        }


# ==================== STARTUP/SHUTDOWN ====================

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print("Medical Clinic Chatbot API Starting...")
    print("=" * 60)
    print(f"Clinic: {CLINIC_CONFIG['name']}")
    print(f"Model: {MODEL_NAME}")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    # Initialize database session for chatbot conversation tracking
    db = SessionLocal()
    chatbot.set_db(db)
    print("✅ Chatbot conversation tracking enabled (database connected)")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\nShutting down Medical Clinic Chatbot API...")


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
