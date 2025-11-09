from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ChatHistoryPart(BaseModel):
    """Part of a chat message (text, image, etc.)"""
    text: str = Field(..., description="Text content of the message part")


class ChatHistoryMessage(BaseModel):
    """Single message in chat history"""
    role: str = Field(..., description="Role: 'user' or 'model'")
    parts: List[ChatHistoryPart] = Field(..., description="Message parts (typically text)")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    chat_history: Optional[List[ChatHistoryMessage]] = Field(
        None, 
        description="Chat history in Gemini API format"
    )
    # Keep for backward compatibility


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
    chat_history: Optional[List[ChatHistoryMessage]] = Field(
        None, 
        description="Chat history in Gemini API format"
    )
    # Keep for backward compatibility
    content: Optional[List[Dict[str, Any]]] = Field(None, description="Additional content such as symptoms or context (deprecated)")

class HistoryResponse(BaseModel):
    """Response model for conversation history"""
    session_id: str
    messages: List[Dict[str, str]]


