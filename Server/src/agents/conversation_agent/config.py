from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)
from .prompts import CONVERSATION_SYSTEM_PROMPT


class ConversationModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing Conversation LLM model...")
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.6,  # More natural and friendly
                top_p=0.95,
                top_k=40,
                max_tokens=1024,
            )
            
            print(f"Conversation model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_conversation_model():
    return ConversationModelSingleton.get_instance()


# Conversation-specific generation config
CONVERSATION_GENERATION_CONFIG = {
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}