"""
Image Analyzer Agent Configuration
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os


class ImageAnalyzerModelSingleton:
    """Singleton for Image Analyzer's LLM model"""
    _instance: Optional[ChatGoogleGenerativeAI] = None
    
    @classmethod
    def get_instance(cls) -> ChatGoogleGenerativeAI:
        if cls._instance is None:
            print("🖼️  Initializing Image Analyzer LLM model...")
            if GOOGLE_API_KEY:
                os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
            
            cls._instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                temperature=0.4,  # Balanced for image description
                top_p=0.95,
                top_k=40,
                max_tokens=1536,
            )
            print(f"✅ Image Analyzer model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_image_analyzer_model() -> ChatGoogleGenerativeAI:
    """Get singleton Image Analyzer LLM instance"""
    return ImageAnalyzerModelSingleton.get_instance()
