from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import SYMPTOM_EXTRACTOR_SYSTEM_PROMPT


class SymptomExtractorModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            
            cls._instance = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.2,  # Very conservative for accurate extraction
                top_p=0.85,
                top_k=40,
                max_tokens=5048,  # Larger for detailed structured output
                model_kwargs={"response_mime_type": "application/json"}  # Force JSON output
            )
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_symptom_extractor_model():
    return SymptomExtractorModelSingleton.get_instance()
