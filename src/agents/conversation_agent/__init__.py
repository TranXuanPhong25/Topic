"""Conversation Agent - General conversation and FAQ handling"""
from src.agents.conversation_agent.config import get_conversation_model
from .conversation_agent import ConversationAgentNode

def new_conversation_agent_node(knowledge_base):
    model = get_conversation_model()
    return ConversationAgentNode(model, knowledge_base=knowledge_base)
__all__ = ["ConversationAgentNode", "new_conversation_agent_node"]
