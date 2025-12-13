"""
Document Retriever Helper Functions

Provides utility functions for agents to call the document retriever.
"""
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from src.models.state import GraphState


def can_call_retriever(state: "GraphState", agent_name: str) -> bool:
    """
    Check if an agent can call the document retriever.
    
    Each agent is limited to max_retriever_calls_per_agent calls (default: 2).
    
    Args:
        state: Current graph state
        agent_name: Name of the agent wanting to call retriever
        
    Returns:
        True if agent can call retriever, False otherwise
    """
    max_calls = state.get("max_retriever_calls_per_agent", 2)
    call_counts = state.get("retriever_call_counts", {})
    current_count = call_counts.get(agent_name, 0)
    
    return current_count < max_calls


def request_document_retrieval(
    state: "GraphState",
    agent_name: str,
    query: Optional[str] = None
) -> Tuple["GraphState", bool]:
    """
    Request document retrieval from an agent.
    
    This function:
    1. Checks if the agent can still call the retriever
    2. Updates the call count
    3. Sets up the state for document retriever to process
    
    Args:
        state: Current graph state
        agent_name: Name of the calling agent
        query: Optional specific query (if None, retriever will build from state)
        
    Returns:
        Tuple of (updated_state, success)
        - success is True if retrieval request was accepted
        - success is False if agent has exceeded max calls
    """
    if not can_call_retriever(state, agent_name):
        max_calls = state.get("max_retriever_calls_per_agent", 2)
        print(f"{agent_name} has already called document_retriever {max_calls} times (max)")
        return state, False
    
    # Update call count
    call_counts = state.get("retriever_call_counts", {})
    call_counts[agent_name] = call_counts.get(agent_name, 0) + 1
    state["retriever_call_counts"] = call_counts
    
    # Set up retriever call
    state["retriever_caller"] = agent_name
    if query:
        state["retriever_query"] = query
    
    print(f"📤 {agent_name} requesting document retrieval (call {call_counts[agent_name]}/{state.get('max_retriever_calls_per_agent', 2)})")
    
    return state, True


def get_retriever_call_count(state: "GraphState", agent_name: str) -> int:
    """
    Get the number of times an agent has called the document retriever.
    
    Args:
        state: Current graph state
        agent_name: Name of the agent
        
    Returns:
        Number of calls made by the agent
    """
    call_counts = state.get("retriever_call_counts", {})
    return call_counts.get(agent_name, 0)


def has_retrieved_documents(state: "GraphState") -> bool:
    """
    Check if there are retrieved documents in the state.
    
    Args:
        state: Current graph state
        
    Returns:
        True if there are retrieved documents
    """
    docs = state.get("retrieved_documents", [])
    return len(docs) > 0


def get_document_synthesis(state: "GraphState") -> dict:
    """
    Get the document synthesis from the state.
    
    Args:
        state: Current graph state
        
    Returns:
        Document synthesis dict or empty dict
    """
    return state.get("document_synthesis", {})
