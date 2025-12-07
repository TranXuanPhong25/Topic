"""Recommender Node: Synthesizes investigations and retrieved context to generate final recommendations."""
import json
from typing import TYPE_CHECKING, Dict

from src.configs.agent_config import SystemMessage, HumanMessage
from src.agents.document_retriever.helpers import (
    can_call_retriever,
    request_document_retrieval,
    has_retrieved_documents,
    get_document_synthesis
)
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
        retrieved_documents = state.get("retrieved_documents", [])
        document_synthesis = get_document_synthesis(state)
        
        try:
            # Check if we need document retrieval for better recommendations
            # Request retrieval if we don't have documents and can still call
            if not has_retrieved_documents(state) and can_call_retriever(state, "recommender"):
                primary_condition = diagnosis.get("primary_diagnosis", {}).get("condition", "")
                if primary_condition:
                    query = f"Khuyến nghị điều trị và chăm sóc cho {primary_condition}"
                    state, success = request_document_retrieval(state, "recommender", query)
                    if success:
                        state["next_step"] = "document_retriever"
                        print(f"📚 Recommender: Requesting document retrieval for recommendations")
                        return state
            
            # Get goal and context from current plan step
            goal = self._get_current_goal(state)
            context_data = self._get_current_context(state)
            
            # Include document synthesis in prompt if available
            synthesis_info = ""
            if document_synthesis:
                main_findings = document_synthesis.get("synthesis", {}).get("main_findings", "")
                key_points = document_synthesis.get("synthesis", {}).get("key_points", [])
                if main_findings or key_points:
                    synthesis_info = f"\n\n📚 Thông tin từ tài liệu y khoa:\n{main_findings}"
                    if key_points:
                        synthesis_info += f"\nĐiểm chính: {', '.join(key_points)}"
            
            recommendation_prompt = build_recommender_prompt(
                diagnosis, 
                risk_assessment, 
                goal,
                context_data.get("context", "") + synthesis_info,
                context_data.get("user_context", "")
            )

            messages = [
                SystemMessage(content=RECOMMENDER_SYSTEM_PROMPT),
                HumanMessage(content=recommendation_prompt)
            ]
            response = self.gemini_model.invoke(messages)
            recommendation = response.content.strip()
            print(recommendation)
            state["recommendation"] = recommendation
            state["current_step"] += 1
            state["next_step"] = "supervisor"  # Default: return to supervisor

            
        except Exception as e:
            print(f"Recommender error: {str(e)}")
            state["recommendation"] = "Vui lòng gặp bác sĩ để được tư vấn chi tiết."
            state["final_response"] = state["recommendation"]
            state["next_step"] = "supervisor"
        
        return state
    

