"""
Synthesis Agent Configuration
"""
from typing import Optional, Any
import google.generativeai as genai
from src.configs.agent_config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from .prompts import SYNTHESIS_SYSTEM_PROMPT


class SynthesisModelSingleton:
    """Singleton for Synthesis agent's LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("📊 Initializing Synthesis LLM model...")
            genai.configure(api_key=GOOGLE_API_KEY)
            
            generation_config = genai.GenerationConfig(
                temperature=0.3,  # Conservative for medical synthesis
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,  # Larger for comprehensive reports
            )
            
            cls._instance = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config=generation_config,
                system_instruction=SYNTHESIS_SYSTEM_PROMPT
            )
            print(f"✅ Synthesis model initialized: {GEMINI_MODEL_NAME}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_synthesis_model():
    """Get singleton Synthesis LLM instance"""
    return SynthesisModelSingleton.get_instance()
