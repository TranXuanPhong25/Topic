from typing import List, Dict, Any, Optional
from src.configs.agent_config import BaseMessage, SystemMessage, HumanMessage, AIMessage


def build_messages_with_history(
    system_prompt: str,
    current_prompt: str,
    chat_history: Optional[List[Dict[str, Any]]] = None,
    image_base64: Optional[str] = None
) -> List[BaseMessage]:
    """
    Build a list of messages including system prompt, chat history, and current prompt.
    Supports images via image_base64 parameter.
    """
    messages: List[BaseMessage] = [SystemMessage(content=system_prompt)] if system_prompt else []
    
    # Add chat history as message pairs if available
    if chat_history:
        for msg in chat_history:
            role = msg.get("role")
            text_parts = [part.get("text", "") for part in msg.get("parts", [])]
            text = " ".join(text_parts)
            
            if not text:
                continue
            
            if role == "user":
                messages.append(HumanMessage(content=text))
            elif role in ("model", "assistant"):
                messages.append(AIMessage(content=text))
    
    # Add current prompt with optional image
    if image_base64:
        # Build multi-part content with text and image
        content = [
            {"type": "text", "text": current_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
        messages.append(HumanMessage(content=content))
    else:
        messages.append(HumanMessage(content=current_prompt))
    
    return messages


def extract_text_from_gemini_message(msg: Dict[str, Any]) -> str:
    """
    Extract text content from a Gemini-format message.
    """
    text_parts = [part.get("text", "") for part in msg.get("parts", [])]
    return " ".join(text_parts).strip()


def extract_text_from_content(content: Any) -> str:
    """
    Extract text from various content formats (Gemini 2.5 style).
    """
    if content is None:
        return ""
    
    # Plain string
    if isinstance(content, str):
        return content.strip()
    
    # List of content blocks (Gemini 2.5 format)
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                # Content block with 'text' key
                if 'text' in block:
                    text_parts.append(block['text'])
                # Fallback to other common keys
                elif 'content' in block:
                    text_parts.append(str(block['content']))
            elif isinstance(block, str):
                text_parts.append(block)
        return " ".join(text_parts).strip()
    
    # Dict with 'text' key
    if isinstance(content, dict):
        if 'text' in content:
            return str(content['text']).strip()
        if 'content' in content:
            return str(content['content']).strip()
    
    # Fallback: convert to string
    return str(content).strip()
