"""
Image Analyzer Agent Configuration
"""
from typing import Optional

from src.agents.image_analyzer.gemini_vision_analyzer import GeminiVisionAnalyzer
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, ChatGoogleGenerativeAI
import os


class ImageAnalyzerModelSingleton:
    """Singleton for Image Analyzer's LLM model"""
    _instance: Optional[GeminiVisionAnalyzer] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🔬 Initializing Investigation Generator LLM model...")
            
            model = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL_NAME,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3,  # Conservative for medical tests
                top_p=0.9,
                top_k=40,
                max_tokens=1536,
            )
            cls._instance = GeminiVisionAnalyzer(model)
        return cls._instance
    @classmethod
    def reset(cls):
        cls._instance = None


def get_image_analyzer_model() -> GeminiVisionAnalyzer:
    """Get singleton Image Analyzer LLM instance"""
    return ImageAnalyzerModelSingleton.get_instance()
