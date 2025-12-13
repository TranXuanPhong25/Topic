from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import SYNTHESIS_SYSTEM_PROMPT


class SynthesisModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing Synthesis LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3,  # Conservative for medical synthesis
                top_p=0.9,
                top_k=40,
                max_tokens=2048,  # Larger for comprehensive reports
            )
            print(f"Synthesis model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_synthesis_model():
    return SynthesisModelSingleton.get_instance()
