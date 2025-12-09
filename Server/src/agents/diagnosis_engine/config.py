"""
Diagnosis Engine Configuration
Handles medical diagnosis based on symptoms
"""
from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import DIAGNOSIS_SYSTEM_PROMPT


class DiagnosisModelSingleton:
    """Singleton for Diagnosis Engine's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🏥 Initializing Diagnosis Engine LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.24,  # Conservative for medical diagnosis
                top_p=0.9,
                top_k=40,
                max_tokens=3048,
            )
            print(f"✅ Diagnosis model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_diagnosis_model():
    """Get singleton Diagnosis Engine LLM instance"""
    return DiagnosisModelSingleton.get_instance()


# Diagnosis-specific generation config
DIAGNOSIS_GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
}
