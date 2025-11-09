"""
Appointment Scheduler Agent Configuration
"""
from typing import Optional
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import google.generativeai as genai
import os
from typing import Any

class AppointmentModelSingleton:
    """Singleton for Appointment Scheduler's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls) -> Any:
        if cls._instance is None:
            print("📅 Initializing Appointment Scheduler LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.6,  # More natural and friendly
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
            )
            print(f"✅ Appointment model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_appointment_model() -> Any:
    """Get singleton Appointment Scheduler LLM instance"""
    return AppointmentModelSingleton.get_instance()
