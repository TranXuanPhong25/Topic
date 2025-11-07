"""
Recommender Node: Synthesizes investigations and retrieved context to generate final recommendations.
"""
import json
from typing import TYPE_CHECKING

from .prompts import build_recommender_prompt

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class RecommenderNode:
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("================ Recommender Agent =================")
        
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        # investigation_plan = state.get("investigation_plan", [])
        retrieved_documents = state.get("retrieved_documents", [])
        try:
            recommendation_prompt = build_recommender_prompt(diagnosis, risk_assessment)
            # **Tài liệu tham khảo:**
            # {len(retrieved_documents)} documents retrieved"""

            response = self.gemini_model.generate_content(recommendation_prompt)
            recommendation = response.text.strip()
            print(recommendation)
            state["recommendation"] = recommendation
            state["current_step"] +=1

            
        except Exception as e:
            print(f"Recommender error: {str(e)}")
            state["recommendation"] = "Vui lòng gặp bác sĩ để được tư vấn chi tiết."
            state["final_response"] = state["recommendation"]
        
        return state
    

