"""
Router Agent Configuration
Handles intent classification and routing decisions
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import ROUTER_SYSTEM_PROMPT


class RouterModelSingleton:
    """Singleton for Router agent's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🔀 Initializing Router LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.2,  # Very precise for classification
                top_p=0.9,
                top_k=40,
                max_output_tokens=512,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=ROUTER_SYSTEM_PROMPT
            )
            print(f"✅ Router model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_router_model():
    """Get singleton Router LLM instance"""
    return RouterModelSingleton.get_instance()


# Router-specific generation config
ROUTER_GENERATION_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 512,
}
