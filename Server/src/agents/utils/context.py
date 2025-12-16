from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.state import GraphState


def get_current_context(state: "GraphState") -> Dict[str, str]:
    """
    Extract context and user_context for the current step from the plan.
    
    Args:
        state: Current graph state
        
    Returns:
        Dict with 'context' and 'user_context' keys (empty strings if not found)
    """
    plan = state.get("plan", [])
    current_step_index = state.get("current_step", 0)
    
    if not plan or current_step_index >= len(plan):
        return {"context": "", "user_context": ""}
    
    current_plan_step = plan[current_step_index]
    context = current_plan_step.get("context", "")
    user_context = current_plan_step.get("user_context", "")
    
    if context:
        print(f"Context: {context[:100]}...")
    if user_context:
        print(f"User Context: {user_context[:100]}...")
    
    return {"context": context, "user_context": user_context}


def get_current_goal(state: "GraphState") -> str:
    """
    Extract the goal for the current step from the plan.
    
    Args:
        state: Current graph state
        
    Returns:
        Goal string (empty string if not found)
    """
    plan = state.get("plan", [])
    current_step_index = state.get("current_step", 0)
    
    if not plan or current_step_index >= len(plan):
        return ""
    
    current_plan_step = plan[current_step_index]
    goal = current_plan_step.get("goal", "")
    
    if goal:
        print(f"Current Goal: {goal}")
    
    return goal
