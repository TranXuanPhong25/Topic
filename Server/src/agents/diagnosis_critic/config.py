from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import DIAGNOSIS_CRITIC_SYSTEM_PROMPT


class DiagnosisCriticModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing Diagnosis Engine LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3,  # Conservative for medical diagnosis
                top_p=0.9,
                top_k=40,
                max_tokens=6048,
            )
            print(f"Diagnosis model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_diagnosis_critic_model():
    return DiagnosisCriticModelSingleton.get_instance()


