"""
Guardrail Model Configuration
Uses a lightweight model specifically for guardrail checks to reduce rate limiting
"""
import pickle
from typing import Optional, Any
from src.configs.agent_config import GOOGLE_API_KEY, ChatGoogleGenerativeAI


class GuardrailModelSingleton:
    """Singleton for lightweight guardrail LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",  
                google_api_key=GOOGLE_API_KEY,
                temperature=0.1,  
                top_p=0.8,
                top_k=20,
                max_tokens=4024,
            )
            
            print(f"Guardrail model initialized: gemini-2.5-flash-lite")
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_guardrail_model():
    """Get singleton lightweight Guardrail LLM instance"""
    return GuardrailModelSingleton.get_instance()



class PromptInjectionDetectorSingleton:
    """Singleton for lightweight guardrail LLM model"""
    _instance: Optional[Any] = None
    
    @classmethod
    def get_instance(cls) -> Any:
        if cls._instance is None:
            with open('./thevgergroup/prompt_protect/skops-3fs68p31.pkl', 'rb') as f: 
                cls._instance = pickle.load(f)
        return cls._instance
    
    @classmethod
    def reset(cls):
        cls._instance = None


def get_prompt_injection_detector():
    """Get singleton lightweight Guardrail LLM instance"""
    return PromptInjectionDetectorSingleton.get_instance()
