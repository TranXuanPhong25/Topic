"""
Document Retriever Agent Configuration
"""
from typing import Any, Optional
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)


class DocumentRetrieverModelSingleton:
    """Singleton for Document Retriever's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls) -> Any:
        if cls._instance is None:
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.6,  # More natural and friendly
                top_p=0.95,
                top_k=40,
                max_tokens=1024,
            )
            print(f"✅ Document Retriever model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_document_retriever_model() -> Any:
    """Get singleton Document Retriever LLM instance"""
    return DocumentRetrieverModelSingleton.get_instance()
