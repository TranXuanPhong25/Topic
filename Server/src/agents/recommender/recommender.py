"""Recommender Node: Synthesizes investigations and retrieved context to generate final recommendations."""
import json
from typing import TYPE_CHECKING, Dict

from src.configs.agent_config import SystemMessage, HumanMessage
from .prompts import build_recommender_prompt, RECOMMENDER_SYSTEM_PROMPT

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class RecommenderNode:
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
    
    def _get_current_goal(self, state: "GraphState") -> str:
        """
        Extract the goal for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Goal string or empty string if not found
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return ""
        
        current_plan_step = plan[current_step_index]
        goal = current_plan_step.get("goal", "")
        
        if goal:
            print(f"🎯 Current Goal: {goal}")
        
        return goal
    
    def _get_current_context(self, state: "GraphState") -> Dict[str, str]:
        """
        Extract context and user_context for the current step from the plan
        
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
            print(f"📝 Context: {context[:100]}...")
        if user_context:
            print(f"👤 User Context: {user_context[:100]}...")
        
        return {"context": context, "user_context": user_context}
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("================ Recommender Agent =================")
        
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        # investigation_plan = state.get("investigation_plan", [])
        retrieved_documents = state.get("retrieved_documents", [])
        try:
            # Get goal and context from current plan step
            goal = self._get_current_goal(state)
            context_data = self._get_current_context(state)
            
            recommendation_prompt = build_recommender_prompt(
                diagnosis, 
                risk_assessment, 
                goal,
                context_data.get("context", ""),
                context_data.get("user_context", "")
            )
            # **Tài liệu tham khảo:**
            # {len(retrieved_documents)} documents retrieved"""

            messages = [
                SystemMessage(content=RECOMMENDER_SYSTEM_PROMPT),
                HumanMessage(content=recommendation_prompt)
            ]
            response = self.gemini_model.invoke(messages)
            recommendation = response.content.strip()
            print(recommendation)
            state["recommendation"] = recommendation
            state["current_step"] +=1

            
        except Exception as e:
            print(f"Recommender error: {str(e)}")
            state["recommendation"] = "Vui lòng gặp bác sĩ để được tư vấn chi tiết."
            state["final_response"] = state["recommendation"]
        
        return state
    

