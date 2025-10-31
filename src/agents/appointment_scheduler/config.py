"""
Appointment Scheduler Agent Configuration
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os


class AppointmentModelSingleton:
    """Singleton for Appointment Scheduler's LLM model"""
    _instance: Optional[ChatGoogleGenerativeAI] = None
    
    @classmethod
    def get_instance(cls) -> ChatGoogleGenerativeAI:
        if cls._instance is None:
            print("📅 Initializing Appointment Scheduler LLM model...")
            if GOOGLE_API_KEY:
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                temperature=0.3,  # Precise for scheduling
                top_p=0.9,
                top_k=40,
                max_tokens=1024,
            )
            print(f"✅ Appointment model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_appointment_model() -> ChatGoogleGenerativeAI:
    """Get singleton Appointment Scheduler LLM instance"""
    return AppointmentModelSingleton.get_instance()
