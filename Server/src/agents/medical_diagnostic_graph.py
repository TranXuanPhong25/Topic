from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional
from typing import List
from src.agents.diagnosis_critic import new_diagnosis_crictic_node
from src.models.state import GraphState

from src.agents.supervisor import new_supervisor_node

from src.knowledges.knowledge_base import FAQKnowledgeBase

from src.agents.conversation_agent import ConversationAgentNode, new_conversation_agent_node
from src.agents.appointment_scheduler import AppointmentSchedulerNode, new_appointment_scheduler_node
from src.agents.image_analyzer import ImageAnalyzerNode, new_image_analyzer_node
from src.agents.symptom_extractor import SymptomExtractorNode, new_symptom_extractor_node
from src.agents.diagnosis_engine import DiagnosisEngineNode, new_diagnosis_engine_node
from src.agents.investigation_generator import InvestigationGeneratorNode, new_investigation_generator_node
from src.agents.document_retriever import DocumentRetrieverNode, new_document_retriever_node
from src.agents.recommender import RecommenderNode, new_recommender_node
from src.agents.synthesis import SynthesisNode, new_synthesis_node
from src.agents.conversation_agent import new_conversation_agent_node
from src.agents.appointment_scheduler import  new_appointment_scheduler_node
from src.agents.image_analyzer import new_image_analyzer_node
from src.agents.symptom_extractor import new_symptom_extractor_node
from src.agents.diagnosis_engine import new_diagnosis_engine_node
from src.agents.investigation_generator import  new_investigation_generator_node
from src.agents.document_retriever import  new_document_retriever_node
from src.agents.recommender import  new_recommender_node
from src.agents.synthesis import  new_synthesis_node


class MedicalDiagnosticGraph:
    def __init__(self):

        # Initialize components
        self.knowledge_base = FAQKnowledgeBase()

        self.conversation_agent_node = new_conversation_agent_node(self.knowledge_base)
        self.appointment_scheduler_node = new_appointment_scheduler_node()
        self.image_analyzer_node = new_image_analyzer_node()
        self.symptom_extractor_node = new_symptom_extractor_node()
        self.diagnosis_engine_node = new_diagnosis_engine_node()
        self.investigation_generator_node = new_investigation_generator_node()
        self.document_retriever_node = new_document_retriever_node()
        self.recommender_node = new_recommender_node()
        self.synthesis_node = new_synthesis_node()
        self.diagnosis_critic_node = new_diagnosis_crictic_node()
        self.supervisor_node = new_supervisor_node()
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("conversation_agent", self.conversation_agent_node)
        workflow.add_node("appointment_scheduler", self.appointment_scheduler_node)
        workflow.add_node("image_analyzer", self.image_analyzer_node)
        workflow.add_node("symptom_extractor", self.symptom_extractor_node)
        workflow.add_node("diagnosis_engine", self.diagnosis_engine_node)
        workflow.add_node("investigation_generator", self.investigation_generator_node)
        workflow.add_node("document_retriever", self.document_retriever_node)
        workflow.add_node("recommender", self.recommender_node)
        workflow.add_node("synthesis", self.synthesis_node)
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("diagnosis_critic", self.diagnosis_critic_node)
        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            lambda s: s["next_step"],
            {
                "conversation_agent": "conversation_agent",
                "appointment_scheduler": "appointment_scheduler",
                "image_analyzer": "image_analyzer",
                "symptom_extractor": "symptom_extractor",
                "diagnosis_engine": "diagnosis_engine",
                "investigation_generator": "investigation_generator",
                "recommender": "recommender",
                "synthesis": "synthesis",
                "END" : END,

            }   
        )

        workflow.add_edge("symptom_extractor","supervisor")
        workflow.add_edge("conversation_agent", END)
        workflow.add_edge("image_analyzer", "supervisor")
        workflow.add_edge("appointment_scheduler", END)
        workflow.add_edge("investigation_generator", "supervisor")
        
        # Document retriever returns to the agent that called it
        workflow.add_conditional_edges(
            "document_retriever",
            lambda s: s.get("retriever_caller") or "supervisor",
            {
                "supervisor": "supervisor",
                "diagnosis_engine": "diagnosis_engine",
                "diagnosis_critic": "diagnosis_critic",
                "recommender": "recommender",
            }
        )
        
        # Recommender and diagnosis_engine can call document_retriever
        workflow.add_conditional_edges(
            "recommender",
            lambda s: s.get("next_step") or "supervisor",
            {
                "supervisor": "supervisor",
                "document_retriever": "document_retriever",
            }
        )
        
        workflow.add_conditional_edges(
            "diagnosis_engine",
            lambda s: s.get("next_step") or "diagnosis_critic",
            {
                "diagnosis_critic": "diagnosis_critic",
                "document_retriever": "document_retriever",
            }
        )
        
        workflow.add_edge("synthesis", END)
        workflow.add_conditional_edges(
            "diagnosis_critic",
            lambda s: s["next_step"],
            {
                "supervisor": "supervisor",
                "diagnosis_engine": "diagnosis_engine",
                "document_retriever": "document_retriever",
            }
        )
        
        return workflow.compile()

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    async def analyze(
            self,
            user_input: str,
            image: Optional[str] = None,
            chat_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        # Initialize state
        initial_state: GraphState = {
            "input": user_input,
            "chat_history": chat_history or [],
            
            "image": image,
            "image_type": None,
            "is_diagnostic_image": None,
            "image_analysis_intent": None,
            "symptom_extractor_input" : "",
            "symptoms": {},
            
            "image_analysis_result": {},
            
            "diagnosis": {},
            "information_needed": None,
            "risk_assessment": {},
            # Revision tracking
            "revision_count": 0,
            "max_revisions": 2,
            "revision_requirements": None,
            "detailed_review": None,
            
            "investigation_plan": [],
            "retrieved_documents": [],
            "rag_answer": "",
            "rag_english_query": "",
            "document_synthesis": {},
            # Document retrieval tracking
            "retriever_caller": None,
            "retriever_query": None,
            "retriever_call_counts": {},
            "max_retriever_calls_per_agent": 2,
            
            "recommendation": "",
            
            "final_response": "",
            "intermediate_messages": [],
            "plan": [],
            "current_step": 0,
            "next_step": None,
        }

        try:
            final_state = await self.graph.ainvoke(initial_state, config={"recursion_limit": 25})

            return {
                "success": True,
                "final_response": final_state["final_response"],
            }

        except Exception as e:
            print(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Sorry, an error occurred processing your request. Please try again or contact the clinic.",
                "error": str(e),
            }

    async def analyze_stream(
            self,
            user_input: str,
            image: Optional[str] = None,
            chat_history: Optional[list] = None,
            on_intermediate=None,
    ) -> Dict[str, Any]:        
        initial_state: GraphState = {
            "input": user_input,
            "chat_history": chat_history or [],
            "symptom_extractor_input": "",
            "image": image,
            "image_type": None,
            "is_diagnostic_image": None,
            "image_analysis_intent": None,
            "symptoms": {},
            "image_analysis_result": {},
            "diagnosis": {},
            "risk_assessment": {},
            "information_needed": None,
            "revision_count": 0,
            "max_revisions": 2,
            "revision_requirements": None,
            "detailed_review": None,
            "investigation_plan": [],
            "retrieved_documents": [],
            "rag_answer": "",
            "rag_english_query": "",
            "document_synthesis": {},
            # Document retrieval tracking
            "retriever_caller": None,
            "retriever_query": None,
            "retriever_call_counts": {},
            "max_retriever_calls_per_agent": 2,
            "recommendation": "",
            "final_response": "",
            "plan": [],
            "current_step": 0,
            "next_step": None,
            "intermediate_messages": [],  # Track intermediate messages for streaming
        }

        try:
            final_state = await self.graph.ainvoke(initial_state, config={"recursion_limit": 25})

            return {
                "success": True,
                "final_response": final_state["final_response"],
                "intermediate_messages": final_state.get("intermediate_messages", []),
            }

        except Exception as e:
            print(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Sorry, an error occurred processing your request. Please try again or contact the clinic.",
                "intermediate_messages": [],
                "error": str(e),
            }