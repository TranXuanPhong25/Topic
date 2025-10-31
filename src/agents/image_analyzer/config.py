"""
Image Analyzer Agent Configuration
"""
from typing import Optional

from google.generativeai.generative_models import GenerativeModel

from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
import os
import google.generativeai as genai


class ImageAnalyzerModelSingleton:
    """Singleton for Image Analyzer's LLM model"""
    _instance: Optional[GenerativeModel] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🔬 Initializing Investigation Generator LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.3,  # Conservative for medical tests
                top_p=0.9,
                top_k=40,
                max_output_tokens=1536,
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
            )
        return cls._instance
    @classmethod
    def reset(cls):
        cls._instance = None


def get_image_analyzer_model() -> ChatGoogleGenerativeAI:
    """Get singleton Image Analyzer LLM instance"""
    return ImageAnalyzerModelSingleton.get_instance()
