import operator
from typing import Literal, Optional, Dict, TypedDict, Any, List, Annotated, TypeAlias
# ============================================================================
# GRAPH STATE DEFINITION (As specified in requirements)
# ============================================================================
Intention: TypeAlias = Literal[
    "normal_conversation",
    "needs_examiner",
    "image_and_symptoms",
    "symptoms_only",
    "not_classified",
]
class GraphState(TypedDict):
    """
    Comprehensive state for the medical AI system graph.
    All data flows through this shared state according to the diagram.
    """
    # Input and routing
    input: str  # Initial user query
    intent: Intention # normal_conversation, needs_examiner, symptoms_only, image_and_symptoms
    
    # Image and symptoms
    image: Optional[str]  # Base64 encoded image
    symptoms: Dict[str, Any]  # Extracted symptoms from input
    
    # Vision analysis
    image_analysis_result: Dict[str, Any]  # Output from ImageAnalyzerF
    
    # Combined analysis
    combined_analysis: str  # Merged symptoms and image analysis
    
    # Diagnosis and risk
    diagnosis: Dict[str, Any]  # Output from DiagnosisEngine
    risk_assessment: Dict[str, Any]  # Output from RiskAssessor
    information_needed: Optional[Dict[str, Any]]  # Missing info for accurate diagnosis
    
    # Investigation and retrieval
    investigation_plan: List[Dict[str, Any]]  # Generated list of investigations
    retrieved_documents: List[Dict[str, Any]]  # Context from Vector DB and KG
    
    # Recommendations
    recommendation: str  # Final actionable advice
    
    # Conversation and appointment
    conversation_output: str  # Result from ConversationAgent
    appointment_details: Dict[str, Any]  # Result from AppointmentScheduler
    
    # Final output
    final_response: str  # Message to be sent to user
    
    # Logging and metadata
    messages: Annotated[List[str], operator.add]  # Append-only log
    metadata: Dict[str, Any]  # Additional context

    plan: List[Dict[str, Any]]  # Added for plan storage
    current_step: int  # Added for tracking current step in the plan
    next_step: Optional[str]  # Added for next step identification


