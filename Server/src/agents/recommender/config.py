"""
Recommender Agent Configuration
Provides treatment recommendations and next steps
"""
from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import RECOMMENDER_SYSTEM_PROMPT


class RecommenderModelSingleton:
    """Singleton for Recommender agent's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("💊 Initializing Recommender LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.4,  # Balanced for recommendations
                top_p=0.95,
                top_k=40,
                max_tokens=1536,
            )
            print(f"✅ Recommender model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_recommender_model():
    """Get singleton Recommender LLM instance"""
    return RecommenderModelSingleton.get_instance()


# Recommender-specific generation config
RECOMMENDER_GENERATION_CONFIG = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1536,
}
