"""
Investigation Generator Agent Configuration
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import INVESTIGATION_SYSTEM_PROMPT
from google.generativeai.generative_models import GenerativeModel


class InvestigationModelSingleton:
    """Singleton for Investigation Generator's LLM model"""
    _instance: Optional[GenerativeModel] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🔬 Initializing Investigation Generator LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.3,  # Conservative for medical tests
                top_p=0.9,
                top_k=40,
                max_output_tokens=1536,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=INVESTIGATION_SYSTEM_PROMPT
            )
            print(f"✅ Investigation model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_investigation_model():
    """Get singleton Investigation Generator LLM instance"""
    return InvestigationModelSingleton.get_instance()
