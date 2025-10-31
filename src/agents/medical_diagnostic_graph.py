from langgraph.constants import END
from langgraph.graph import StateGraph
from typing import  Dict, Any, Optional
import google.generativeai as genai
from src.models.state import GraphState
from src.configs.agent_config import (
    DIAGNOSIS_CONFIG,
    get_api_key,
)
from src.agents.supervisor import SupervisorNode, new_supervisor_node

from src.agents.image_analyzer.gemini_vision_analyzer import GeminiVisionAnalyzer
from src.knowledges.knowledge_base import FAQKnowledgeBase
from src.handlers.appointment import AppointmentHandler

from src.agents.router import RouterNode
from src.agents.conversation_agent import ConversationAgentNode, new_conversation_agent_node
from src.agents.appointment_scheduler import AppointmentSchedulerNode, new_appointment_scheduler_node
from src.agents.image_analyzer import ImageAnalyzerNode, new_image_analyzer_node
from src.agents.symptom_extractor import SymptomExtractorNode, new_symptom_extractor_node
from src.agents.combine_analysis import CombineAnalysisNode
from src.agents.diagnosis_engine import DiagnosisEngineNode, new_diagnosis_engine_node
from src.agents.investigation_generator import InvestigationGeneratorNode, new_investigation_generator_node
from src.agents.document_retriever import DocumentRetrieverNode, new_document_retriever_node
from src.agents.recommender import RecommenderNode, new_recommender_node
from src.agents.synthesis import SynthesisNode, new_synthesis_node


class MedicalDiagnosticGraph:
    def __init__(self):
        self.google_api_key = get_api_key()
        
        # Initialize components
        self.vision_analyzer = GeminiVisionAnalyzer(self.google_api_key)
        self.knowledge_base = FAQKnowledgeBase()
        self.appointment_handler = AppointmentHandler()
        
        # Initialize Gemini for text reasoning using centralized config
        genai.configure(api_key=self.google_api_key)
        self.gemini_model = genai.GenerativeModel(
            model_name=DIAGNOSIS_CONFIG["model_name"],
            generation_config=DIAGNOSIS_CONFIG["generation_config"],
            safety_settings=DIAGNOSIS_CONFIG["safety_settings"]
        )

        # Initialize node instances
        # self.router_node = RouterNode(self.gemini_model)
        self.conversation_agent_node = new_conversation_agent_node(self.knowledge_base)
        self.appointment_scheduler_node = new_appointment_scheduler_node(self.appointment_handler)
        self.image_analyzer_node = new_image_analyzer_node()
        self.symptom_extractor_node = new_symptom_extractor_node()
        # self.combine_analysis_node = CombineAnalysisNode()
        self.diagnosis_engine_node = new_diagnosis_engine_node()
        self.investigation_generator_node = new_investigation_generator_node()
        self.document_retriever_node = new_document_retriever_node()
        self.recommender_node = new_recommender_node()
        self.synthesis_node = new_synthesis_node()

        self.supervisor_node = new_supervisor_node()
        # Build the graph
        self.graph = self._build_graph()
        
        print("MedicalDiagnosticGraph initialized successfully")
    
    def _build_graph(self):
        workflow = StateGraph(GraphState)

        # Add all nodes (using node instances)
        # workflow.add_node("router", self.router_node)
        workflow.add_node("conversation_agent", self.conversation_agent_node)
        workflow.add_node("appointment_scheduler", self.appointment_scheduler_node)
        workflow.add_node("image_analyzer", self.image_analyzer_node)
        workflow.add_node("symptom_extractor", self.symptom_extractor_node)
        # workflow.add_node("combine_analysis", self.combine_analysis_node)
        workflow.add_node("diagnosis_engine", self.diagnosis_engine_node)
        workflow.add_node("investigation_generator", self.investigation_generator_node)
        workflow.add_node("document_retriever", self.document_retriever_node)
        workflow.add_node("recommender", self.recommender_node)
        workflow.add_node("synthesis", self.synthesis_node)
        workflow.add_node("supervisor", self.supervisor_node)
        # Build edges using the edge module
        # workflow = build_graph_edges(workflow)
        workflow.set_entry_point("symptom_extractor")
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
        workflow.add_edge("conversation_agent", "supervisor")
        workflow.add_edge("image_analyzer", "supervisor")
        workflow.add_edge("appointment_scheduler", "supervisor")
        workflow.add_edge("diagnosis_engine", "supervisor")
        workflow.add_edge("investigation_generator", "supervisor")
        workflow.add_edge("document_retriever", "supervisor")
        workflow.add_edge("recommender", "supervisor")
        workflow.add_edge("synthesis", "supervisor")  # Synthesis is final step
        # Compile the graph
        return workflow.compile()
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def analyze(
        self,
        user_input: str,
        image: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and return diagnostic results.
        
        Args:
            user_input: User's text input
            image: Optional base64 encoded image
            metadata: Optional additional context
        
        Returns:
            Dictionary containing final_response and full state
        """
        print(f"Starting analysis for input: {user_input[:100]}...")
        
        # Initialize state
        initial_state: GraphState = {
            "input": user_input,
            "image": image,
            "intent": "not_classified",  # Default intent
            "symptoms": {},
            "image_analysis_result": {},
            "combined_analysis": "",
            "diagnosis": {},
            "risk_assessment": {},
            "investigation_plan": [],
            "retrieved_documents": [],
            "recommendation": "",
            "conversation_output": "",
            "appointment_details": {},
            "final_response": "",
            "messages": [],
            "metadata": metadata or {},
            "plan": [],
            "current_step": 0,
            "next_step": None,
        }
        
        try:
            # Execute the graph (returns final state only, not streaming)
            final_state = self.graph.invoke(initial_state, config={"recursion_limit":20})
            
            # Extract only the unique execution steps (final state messages)
            # LangGraph invoke() returns final state, but messages list accumulates all intermediate states
            # Filter to keep only one message per node
            seen_nodes = set()
            cleaned_messages = []
            
            for msg in final_state.get("messages", []):
                # Extract node name from message (e.g., "✅ Router:" -> "Router")
                if ":" in msg:
                    node_part = msg.split(":")[0].replace("✅", "").replace("❌", "").strip()
                    # Create a unique key for this message
                    msg_key = f"{node_part}:{msg.split(':')[1][:50] if ':' in msg else ''}"
                    
                    if msg_key not in seen_nodes:
                        cleaned_messages.append(msg)
                        seen_nodes.add(msg_key)
            
            return {
                "success": True,
                "final_response": final_state["final_response"],
                "intent": final_state.get("intent"),
                "diagnosis": final_state.get("diagnosis"),
                "risk_assessment": final_state.get("risk_assessment"),
                "investigation_plan": final_state.get("investigation_plan"),
                "messages": cleaned_messages,  # Use cleaned messages
                "metadata": final_state.get("metadata", {})
            }
            
        except Exception as e:
            print(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại hoặc liên hệ phòng khám.",
                "error": str(e),
                "messages": [f"❌ Graph execution error: {str(e)}"]
            }

