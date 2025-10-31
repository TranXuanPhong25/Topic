"""
Symptom Extractor Agent Configuration
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import SYMPTOM_EXTRACTOR_SYSTEM_PROMPT


class SymptomExtractorModelSingleton:
    """Singleton for Symptom Extractor's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("🩺 Initializing Symptom Extractor LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.2,  # Very conservative for accurate extraction
                top_p=0.85,
                top_k=40,
                max_output_tokens=2048,  # Larger for detailed structured output
                response_mime_type="application/json",  # Force JSON output
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=SYMPTOM_EXTRACTOR_SYSTEM_PROMPT
            )
            print(f"✅ Symptom Extractor model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_symptom_extractor_model():
    """Get singleton Symptom Extractor LLM instance"""
    return SymptomExtractorModelSingleton.get_instance()
