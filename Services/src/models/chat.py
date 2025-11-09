from pydantic import BaseModel, Field
from typing import Dict, List, Optional
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Conversation session ID")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Bot's response")
    session_id: str = Field(..., description="Conversation session ID")
    timestamp: str = Field(..., description="Response timestamp")


class ImageChatRequest(BaseModel):
    """Request model for image chat endpoint"""
    message: str = Field(..., description="User's text message/symptoms")
    image: str = Field(..., description="Base64 encoded image data (with or without data URI prefix)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

class HistoryResponse(BaseModel):
    """Response model for conversation history"""
    session_id: str
    messages: List[Dict[str, str]]


