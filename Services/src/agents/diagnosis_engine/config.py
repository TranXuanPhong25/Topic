"""
Diagnosis Engine Configuration
Handles medical diagnosis based on symptoms
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import DIAGNOSIS_SYSTEM_PROMPT


class DiagnosisModelSingleton:
    """Singleton for Diagnosis Engine's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🏥 Initializing Diagnosis Engine LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.3,  # Conservative for medical diagnosis
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=DIAGNOSIS_SYSTEM_PROMPT
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
