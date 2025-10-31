"""
Document Retriever Agent Configuration
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os


class DocumentRetrieverModelSingleton:
    """Singleton for Document Retriever's LLM model"""
    _instance: Optional[ChatGoogleGenerativeAI] = None
    
    @classmethod
    def get_instance(cls) -> ChatGoogleGenerativeAI:
        if cls._instance is None:
            print("📚 Initializing Document Retriever LLM model...")
            if GOOGLE_API_KEY:
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                temperature=0.3,  # Precise for retrieval
                top_p=0.9,
                top_k=40,
                max_tokens=1024,
            )
            print(f"✅ Document Retriever model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_document_retriever_model() -> ChatGoogleGenerativeAI:
    """Get singleton Document Retriever LLM instance"""
    return DocumentRetrieverModelSingleton.get_instance()
