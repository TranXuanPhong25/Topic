"""
Combine Analysis Agent Configuration
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os


class CombineAnalysisModelSingleton:
    """Singleton for Combine Analysis's LLM model"""
    _instance: Optional[ChatGoogleGenerativeAI] = None
    
    @classmethod
    def get_instance(cls) -> ChatGoogleGenerativeAI:
        if cls._instance is None:
            print("🔗 Initializing Combine Analysis LLM model...")
            if GOOGLE_API_KEY:
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                temperature=0.3,  # Precise for merging data
                top_p=0.9,
                top_k=40,
                max_tokens=1024,
            )
            print(f"✅ Combine Analysis model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_combine_analysis_model() -> ChatGoogleGenerativeAI:
    """Get singleton Combine Analysis LLM instance"""
    return CombineAnalysisModelSingleton.get_instance()
