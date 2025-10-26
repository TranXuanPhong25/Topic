"""
Centralized configuration for all AI agents in the medical diagnostic system.
This module provides shared settings for model names, API keys, and generation parameters.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# API CONFIGURATION
# ============================================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    )

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Primary model for text-based reasoning and conversation
GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"

# Vision model for image analysis (can be same as primary)
GEMINI_VISION_MODEL_NAME = "gemini-2.5-flash-lite"

# ============================================================================
# GENERATION PARAMETERS
# ============================================================================

# Default generation config for conversational agents
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.4,  # Balanced creativity and consistency
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Generation config for diagnostic tasks (more precise)
DIAGNOSTIC_GENERATION_CONFIG = {
    "temperature": 0.3,  # More conservative for medical diagnosis
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Generation config for vision analysis
VISION_GENERATION_CONFIG = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Generation config for JSON responses
JSON_GENERATION_CONFIG = {
    "temperature": 0.2,  # Very precise for structured output
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# ============================================================================
# SAFETY SETTINGS
# ============================================================================

# Standard safety settings for medical context
# Note: These are permissive to avoid blocking legitimate medical discussions
SAFETY_SETTINGS = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
}

# ============================================================================
# AGENT-SPECIFIC CONFIGURATIONS
# ============================================================================

# Router configuration
ROUTER_CONFIG = {
    "model_name": GEMINI_MODEL_NAME,
    "generation_config": JSON_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# Conversation agent configuration
CONVERSATION_CONFIG = {
    "model_name": GEMINI_MODEL_NAME,
    "generation_config": DEFAULT_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# Diagnosis engine configuration
DIAGNOSIS_CONFIG = {
    "model_name": GEMINI_MODEL_NAME,
    "generation_config": DIAGNOSTIC_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# Vision analyzer configuration
VISION_CONFIG = {
    "model_name": GEMINI_VISION_MODEL_NAME,
    "generation_config": VISION_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# Investigation generator configuration
INVESTIGATION_CONFIG = {
    "model_name": GEMINI_MODEL_NAME,
    "generation_config": DIAGNOSTIC_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# Recommender configuration
RECOMMENDER_CONFIG = {
    "model_name": GEMINI_MODEL_NAME,
    "generation_config": DEFAULT_GENERATION_CONFIG,
    "safety_settings": SAFETY_SETTINGS,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_config(agent_type: str) -> dict:
    """
    Get configuration for a specific agent type.
    
    Args:
        agent_type: One of 'router', 'conversation', 'diagnosis', 
                   'vision', 'investigation', 'recommender'
    
    Returns:
        Configuration dictionary with model_name, generation_config, and safety_settings
    
    Raises:
        ValueError: If agent_type is not recognized
    """
    configs = {
        "router": ROUTER_CONFIG,
        "conversation": CONVERSATION_CONFIG,
        "diagnosis": DIAGNOSIS_CONFIG,
        "vision": VISION_CONFIG,
        "investigation": INVESTIGATION_CONFIG,
        "recommender": RECOMMENDER_CONFIG,
    }
    
    if agent_type not in configs:
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Must be one of: {', '.join(configs.keys())}"
        )
    
    return configs[agent_type].copy()


def get_api_key() -> str:
    """
    Get the Google API key.
    
    Returns:
        Google API key string
    
    Raises:
        ValueError: If API key is not set
    """
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY not found. Please set it in your .env file."
        )
    return GOOGLE_API_KEY


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # API
    "GOOGLE_API_KEY",
    "get_api_key",
    
    # Models
    "GEMINI_MODEL_NAME",
    "GEMINI_VISION_MODEL_NAME",
    
    # Generation configs
    "DEFAULT_GENERATION_CONFIG",
    "DIAGNOSTIC_GENERATION_CONFIG",
    "VISION_GENERATION_CONFIG",
    "JSON_GENERATION_CONFIG",
    
    # Safety
    "SAFETY_SETTINGS",
    
    # Agent configs
    "ROUTER_CONFIG",
    "CONVERSATION_CONFIG",
    "DIAGNOSIS_CONFIG",
    "VISION_CONFIG",
    "INVESTIGATION_CONFIG",
    "RECOMMENDER_CONFIG",
    
    # Helpers
    "get_model_config",
]
