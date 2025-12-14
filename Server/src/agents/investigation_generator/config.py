from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import INVESTIGATION_SYSTEM_PROMPT


class InvestigationModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing Investigation Generator LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3,  # Conservative for medical tests
                top_p=0.9,
                top_k=40,
                max_tokens=5536,
            )
            print(f"Investigation model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_investigation_model():
    return InvestigationModelSingleton.get_instance()
