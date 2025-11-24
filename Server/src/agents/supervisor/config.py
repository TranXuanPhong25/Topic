"""
Router Agent Configuration
Handles intent classification and routing decisions
"""
from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import SUPERVISOR_SYSTEM_PROMPT

class SupervisorModelSingleton:
    """Singleton for Supervisor agent's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.2,  # Very precise for classification
                top_p=0.9,
                top_k=40,
                max_tokens=5120,
            )
            print(f"✅ Supervisor model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_supervisor_model():
    """Get singleton Supervisor LLM instance"""
    return SupervisorModelSingleton.get_instance()

