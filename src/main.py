"""FastAPI server for Medical Clinic Chatbot"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from pydantic import BaseModel
from configs.config import CLINIC_CONFIG
from routes.chat import  chat_router
from routes import faq_router, todo_router
from src.models.health import HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="Medical Clinic Chatbot API",
    description="REST API for AI-powered medical clinic assistant",
    version="1.0.0",
)
app.include_router(faq_router)
app.include_router(todo_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

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
    

@chat_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="gemini-2.0-flash-lite",
        clinic=CLINIC_CONFIG["name"]
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