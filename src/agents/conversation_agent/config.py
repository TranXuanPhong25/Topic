"""
Conversation Agent Configuration
Handles general questions, FAQs, and clinic information
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import CONVERSATION_SYSTEM_PROMPT


class ConversationModelSingleton:
    """Singleton for Conversation agent's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("💬 Initializing Conversation LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.6,  # More natural and friendly
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=CONVERSATION_SYSTEM_PROMPT
            )
            print(f"✅ Conversation model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_conversation_model():
    """Get singleton Conversation LLM instance"""
    return ConversationModelSingleton.get_instance()


# Conversation-specific generation config
CONVERSATION_GENERATION_CONFIG = {
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}
