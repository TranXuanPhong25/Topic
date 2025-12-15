from typing import Optional, Any
from src.configs.agent_config import (
    GOOGLE_API_KEY, 
    GEMINI_MODEL_NAME,
    ChatGoogleGenerativeAI
)


class DocumentRetrieverModelSingleton:
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3,  # Balanced for information synthesis
                top_p=0.9,
                top_k=40,
                max_tokens=8096,  # Larger for detailed document synthesis
                # model_kwargs={"response_mime_type": "application/json"}  # Force JSON output
            )
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_document_retriever_model():
    return DocumentRetrieverModelSingleton.get_instance()
