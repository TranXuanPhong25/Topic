import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    )

# Primary model for text-based reasoning and conversation
GEMINI_MODEL_NAME = "gemini-2.5-pro"

# Vision model for image analysis (can be same as primary)
GEMINI_VISION_MODEL_NAME = "gemini-2.5-flash"

__all__ = [
    # API
    "GOOGLE_API_KEY",
    
    # Models
    "GEMINI_MODEL_NAME",
    # LangChain imports
    "ChatGoogleGenerativeAI",
    "SystemMessage",
    "HumanMessage",
    "AIMessage",
    "BaseMessage",
]
