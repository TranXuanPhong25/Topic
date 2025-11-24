"""Recommender Node: Synthesizes investigations and retrieved context to generate final recommendations."""
import json
from typing import TYPE_CHECKING

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
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("================ Recommender Agent =================")
        
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        # investigation_plan = state.get("investigation_plan", [])
        retrieved_documents = state.get("retrieved_documents", [])
        try:
            # Get goal from current plan step
            goal = self._get_current_goal(state)
            
            recommendation_prompt = build_recommender_prompt(diagnosis, risk_assessment, goal)
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
    

