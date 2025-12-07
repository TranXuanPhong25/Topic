"""
Appointment Scheduler Agent Configuration
"""
from typing import Optional

from langchain.chat_models import init_chat_model

from src.agents.appointment_scheduler.tools import book_appointment, get_available_time_slots, \
    check_appointment_availability
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os
from typing import Any

class AppointmentModelSingleton:
    """Singleton for Appointment Scheduler's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls) -> Any:
        if cls._instance is None:
            model = init_chat_model(GEMINI_MODEL_NAME, model_provider="google_genai")
            cls._instance = model
            print(f"✅ Appointment model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_appointment_model() -> Any:
    """Get singleton Appointment Scheduler LLM instance"""
    return AppointmentModelSingleton.get_instance()