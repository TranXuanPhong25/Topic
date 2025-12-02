"""FastAPI server for Medical Clinic Chatbot"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from pydantic import BaseModel
from src.configs.config import CLINIC_CONFIG
from src.routes.chat import  chat_router
from src.routes import faq_router, todo_router
from src.models.health import HealthResponse
from src.routes.appointments import router as appointment_router

# Initialize FastAPI app
app = FastAPI(
    title="Medical Clinic Chatbot API",
    description="REST API for AI-powered medical clinic assistant",
    version="1.0.0",
)
app.include_router(faq_router)
app.include_router(todo_router)
app.include_router(chat_router)
app.include_router(appointment_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="gemini-2.5-flash-lite",
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