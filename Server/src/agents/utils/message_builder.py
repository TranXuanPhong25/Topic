"""Message builder utilities for constructing chat history and messages."""
from typing import List, Dict, Any, Optional
from src.configs.agent_config import BaseMessage, SystemMessage, HumanMessage, AIMessage


def build_messages_with_history(
    system_prompt: str,
    current_prompt: str,
    chat_history: Optional[List[Dict[str, Any]]] = None
) -> List[BaseMessage]:
    """
    Build a list of messages including system prompt, chat history, and current prompt.
    
    Args:
        system_prompt: System instruction message
        current_prompt: Current user prompt to add
        chat_history: Optional list of chat history in Gemini format
                     Each message should have:
                     - role: "user" or "model"
                     - parts: list of dicts with "text" key
                     
    Returns:
        List of BaseMessage objects (SystemMessage, HumanMessage, AIMessage)
        
    Example:
        >>> messages = build_messages_with_history(
        ...     system_prompt="You are a helpful assistant",
        ...     current_prompt="What is the weather?",
        ...     chat_history=[
        ...         {"role": "user", "parts": [{"text": "Hello"}]},
        ...         {"role": "model", "parts": [{"text": "Hi there!"}]}
        ...     ]
        ... )
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
    
    # Add current prompt
    messages.append(HumanMessage(content=current_prompt))
    
    return messages


def extract_text_from_gemini_message(msg: Dict[str, Any]) -> str:
    """
    Extract text content from a Gemini-format message.
    
    Args:
        msg: Message dict with "parts" key containing list of text parts
        
    Returns:
        Concatenated text from all parts
        
    Example:
        >>> msg = {"role": "user", "parts": [{"text": "Hello"}, {"text": " world"}]}
        >>> extract_text_from_gemini_message(msg)
        'Hello world'
    """
    text_parts = [part.get("text", "") for part in msg.get("parts", [])]
    return " ".join(text_parts).strip()


def extract_text_from_content(content: Any) -> str:
    """
    Extract text from various content formats (Gemini 2.5 style).
    
    Handles:
    - Plain string: "Hello world"
    - List of content blocks: [{'type': 'text', 'text': '...', 'extras': {...}}]
    - Dict with 'text' key: {'type': 'text', 'text': '...'}
    - None or empty
    
    Args:
        content: Content in various formats
        
    Returns:
        Extracted text string
        
    Example:
        >>> extract_text_from_content([{'type': 'text', 'text': 'Hello', 'extras': {'signature': '...'}}])
        'Hello'
        >>> extract_text_from_content("Hello world")
        'Hello world'
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
