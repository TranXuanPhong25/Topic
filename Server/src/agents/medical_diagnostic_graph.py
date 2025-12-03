from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional

from src.agents.diagnosis_critic import new_diagnosis_crictic_node
from src.models.state import GraphState
from src.configs.agent_config import (
    DIAGNOSIS_CONFIG,
    get_api_key,
)
from src.agents.supervisor import SupervisorNode, new_supervisor_node

from src.agents.image_analyzer.gemini_vision_analyzer import GeminiVisionAnalyzer
from src.knowledges.knowledge_base import FAQKnowledgeBase
from src.handlers.appointment import AppointmentHandler

from src.agents.conversation_agent import ConversationAgentNode, new_conversation_agent_node
from src.agents.appointment_scheduler import AppointmentSchedulerNode, new_appointment_scheduler_node
from src.agents.image_analyzer import ImageAnalyzerNode, new_image_analyzer_node
from src.agents.symptom_extractor import SymptomExtractorNode, new_symptom_extractor_node
from src.agents.diagnosis_engine import DiagnosisEngineNode, new_diagnosis_engine_node
from src.agents.investigation_generator import InvestigationGeneratorNode, new_investigation_generator_node
from src.agents.document_retriever import DocumentRetrieverNode, new_document_retriever_node
from src.agents.recommender import RecommenderNode, new_recommender_node
from src.agents.synthesis import SynthesisNode, new_synthesis_node


class MedicalDiagnosticGraph:
    def __init__(self):
        self.google_api_key = get_api_key()

        # Initialize components
        self.knowledge_base = FAQKnowledgeBase()

        # Initialize node instances (using singleton configs)
        # self.router_node = RouterNode(self.gemini_model)
        self.conversation_agent_node = new_conversation_agent_node(self.knowledge_base)
        self.appointment_scheduler_node = new_appointment_scheduler_node()
        self.image_analyzer_node = new_image_analyzer_node()
        self.symptom_extractor_node = new_symptom_extractor_node()
        # self.combine_analysis_node = CombineAnalysisNode()
        self.diagnosis_engine_node = new_diagnosis_engine_node()
        self.investigation_generator_node = new_investigation_generator_node()
        self.document_retriever_node = new_document_retriever_node()
        self.recommender_node = new_recommender_node()
        self.synthesis_node = new_synthesis_node()
        self.diagnosis_critic_node = new_diagnosis_crictic_node()
        self.supervisor_node = new_supervisor_node()
        # Build the graph
        self.graph = self._build_graph()

        print("MedicalDiagnosticGraph initialized successfully")

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
                "document_retriever": "document_retriever",
                "recommender": "recommender",
                "synthesis": "synthesis",
                "END" : END,

            }   
        )

        workflow.add_edge("symptom_extractor","supervisor")
        workflow.add_edge("conversation_agent", END)
        workflow.add_edge("image_analyzer", "supervisor")
        workflow.add_edge("appointment_scheduler", "supervisor")
        workflow.add_edge("investigation_generator", "supervisor")
        workflow.add_edge("document_retriever", "supervisor")
        workflow.add_edge("recommender", "supervisor")
        workflow.add_edge("synthesis", END)
        workflow.add_edge("diagnosis_engine", "diagnosis_critic")
        workflow.add_conditional_edges(
            "diagnosis_critic",
            lambda s: s["next_step"],
            {
                "supervisor": "supervisor",
                "diagnosis_engine": "diagnosis_engine",
            }
        )
        # Compile the graph
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
        """
        Analyze user input and return diagnostic results.
        
        Args:
            user_input: User's text input
            image: Optional base64 encoded image
            chat_history: Optional chat history in Gemini format [{"role": "user", "parts": [{"text": "..."}]}]
        
        Returns:
            Dictionary containing final_response and full state
        """
        print(f"Starting analysis for input: {user_input[:100]}...")
        if chat_history:
            print(f"📝 Received chat history: {len(chat_history)} messages")

        # Initialize state
        initial_state: GraphState = {
            "input": user_input,
            "chat_history": chat_history or [],
            "symptom_extractor_input" : "",
            "image": image,
            "symptoms": {},
            "image_analysis_result": {},
            "diagnosis": {},
            "risk_assessment": {},
            "information_needed": None,
            # Revision tracking
            "revision_count": 0,
            "max_revisions": 2,  # Default: allow up to 2 revisions
            "revision_requirements": None,
            "detailed_review": None,
            "investigation_plan": [],
            "retrieved_documents": [],
            "recommendation": "",
            "final_response": "",
            "plan": [],
            "current_step": 0,
            "next_step": None,
        }

        try:
            # Execute the graph asynchronously (required for async nodes like appointment_scheduler)
            final_state = await self.graph.ainvoke(initial_state, config={"recursion_limit": 20})

            return {
                "success": True,
                "final_response": final_state["final_response"],
            }

        except Exception as e:
            print(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại hoặc liên hệ phòng khám.",
                "error": str(e),
            }