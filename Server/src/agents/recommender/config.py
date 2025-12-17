from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import RECOMMENDER_SYSTEM_PROMPT


class RecommenderModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:            
            cls._instance = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.4,  # Balanced for recommendations
                top_p=0.95,
                top_k=40,
                max_tokens=5536,
            )
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_recommender_model():
    return RecommenderModelSingleton.get_instance()


# Recommender-specific generation config
RECOMMENDER_GENERATION_CONFIG = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1536,
}
