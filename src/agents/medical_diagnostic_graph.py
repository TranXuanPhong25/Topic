"""
LangGraph-based Medical Diagnostic System
Implements the complete diagnostic flow with routing, diagnosis, risk assessment, and recommendations.

Refactored into modular structure with separate nodes and edges.
"""
from langgraph.graph import StateGraph
from typing import  Dict, Any, Optional
import logging
import google.generativeai as genai

from models.state import GraphState
# Import agent configuration
from .config import (
    DIAGNOSIS_CONFIG,
    get_api_key,
)

# Import supporting modules (absolute imports from src package)
from .vision.gemini_vision_analyzer import GeminiVisionAnalyzer
from knowledges.knowledge_base import FAQKnowledgeBase
from handlers.appointment import AppointmentHandler

# Import node implementations
from .nodes import (
    RouterNode,
    ConversationAgentNode,
    AppointmentSchedulerNode,
    ImageAnalyzerNode,
    CombineAnalysisNode,
    DiagnosisEngineNode,
    InvestigationGeneratorNode,
    DocumentRetrieverNode,
    RecommenderNode,
)

# Import edge routing logic
from .edges import build_graph_edges

logger = logging.getLogger(__name__)



# ============================================================================
# MEDICAL DIAGNOSTIC GRAPH - Main Implementation
# ============================================================================

class MedicalDiagnosticGraph:
    """
    Comprehensive medical diagnostic system using LangGraph.
    
    Flow:
    1. Router: Classifies intent and extracts symptoms/image
    2. Conditional branching:
       - normal_conversation → ConversationAgent → END
       - needs_examiner → AppointmentScheduler → END
       - image_and_symptoms → ImageAnalyzer → CombineAnalysis → DiagnosisEngine
       - symptoms_only → DiagnosisEngine
    3. DiagnosisEngine (includes internal RiskAssessor)
    4. Parallel: InvestigationGenerator + DocumentRetriever
    5. Recommender (joins both paths) → END
    """
    
    def __init__(self):
        """
        Initialize the medical diagnostic system.
        
        Args:
            google_api_key: Google API key for Gemini
        """
        
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
        self.router_node = RouterNode(self.gemini_model)
        self.conversation_agent_node = ConversationAgentNode(self.gemini_model, self.knowledge_base)
        self.appointment_scheduler_node = AppointmentSchedulerNode(self.gemini_model, self.appointment_handler)
        self.image_analyzer_node = ImageAnalyzerNode(self.vision_analyzer)
        self.combine_analysis_node = CombineAnalysisNode()
        self.diagnosis_engine_node = DiagnosisEngineNode(self.gemini_model)
        self.investigation_generator_node = InvestigationGeneratorNode(self.gemini_model)
        self.document_retriever_node = DocumentRetrieverNode(self.knowledge_base)
        self.recommender_node = RecommenderNode(self.gemini_model)
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("MedicalDiagnosticGraph initialized successfully")
    
    def _build_graph(self):
        """
        Build the LangGraph workflow according to the diagram.
        
        Graph structure:
        Router (entry) → Conditional branching:
          - ConversationAgent → END
          - AppointmentScheduler → END
          - ImageAnalyzer → CombineAnalysis → DiagnosisEngine → [InvestigationGenerator, DocumentRetriever] → Recommender → END
          - DiagnosisEngine → [InvestigationGenerator, DocumentRetriever] → Recommender → END
        """
        workflow = StateGraph(GraphState)
        
        # Add all nodes (using node instances)
        workflow.add_node("router", self.router_node)
        workflow.add_node("conversation_agent", self.conversation_agent_node)
        workflow.add_node("appointment_scheduler", self.appointment_scheduler_node)
        workflow.add_node("image_analyzer", self.image_analyzer_node)
        workflow.add_node("combine_analysis", self.combine_analysis_node)
        workflow.add_node("diagnosis_engine", self.diagnosis_engine_node)
        workflow.add_node("investigation_generator", self.investigation_generator_node)
        workflow.add_node("document_retriever", self.document_retriever_node)
        workflow.add_node("recommender", self.recommender_node)
        
        # Build edges using the edge module
        workflow = build_graph_edges(workflow)
        
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
        logger.info(f"Starting analysis for input: {user_input[:100]}...")
        
        # Initialize state
        initial_state: GraphState = {
            "input": user_input,
            "image": image,
            "intent": "",
            "symptoms": "",
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
            "metadata": metadata or {}
        }
        
        try:
            # Execute the graph (returns final state only, not streaming)
            final_state = self.graph.invoke(initial_state)
            
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
            logger.error(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại hoặc liên hệ phòng khám.",
                "error": str(e),
                "messages": [f"❌ Graph execution error: {str(e)}"]
            }

