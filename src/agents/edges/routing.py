"""
Routing logic for the Medical Diagnostic Graph.
Handles conditional edges and graph structure.
"""
from models.state import GraphState, Intention
from langgraph.graph import END, StateGraph
class IntentRouter:
    """
    Router for conditional edges based on classified intent.
    """
    
    @staticmethod
    def route_based_on_intent(state: GraphState) -> Intention:
        intent = state.get("intent", "not_classified")
        return intent

def build_graph_edges(workflow: StateGraph) -> StateGraph:
    workflow.set_entry_point("router")
    
    # Conditional edges from Router
    workflow.add_conditional_edges(
        "router",
        IntentRouter.route_based_on_intent,
        {
            "normal_conversation": "conversation_agent",
            "needs_examiner": "appointment_scheduler",
            "image_and_symptoms": "image_analyzer",
            "symptoms_only": "diagnosis_engine",
            "not_classified": END
        }
    )
    
    # Linear edges for image analysis path
    workflow.add_edge("image_analyzer", "combine_analysis")
    workflow.add_edge("combine_analysis", "diagnosis_engine")
    
    # Sequential edges from DiagnosisEngine (to avoid concurrent state updates)
    # First generate investigations, then retrieve documents, then recommend
    workflow.add_edge("diagnosis_engine", "investigation_generator")
    workflow.add_edge("investigation_generator", "document_retriever")
    workflow.add_edge("document_retriever", "recommender")
    
    # End points
    workflow.add_edge("conversation_agent", END)
    workflow.add_edge("appointment_scheduler", END)
    workflow.add_edge("recommender", END)
    
    return workflow
