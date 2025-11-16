from typing import Literal, Optional, Dict, TypedDict, Any, List, Annotated, TypeAlias

class GraphState(TypedDict):
    input: str  # Initial user query
    chat_history: Optional[List[Dict[str, Any]]]  # Chat history in Gemini format
    
    # Image and symptoms
    image: Optional[str]  # Base64 encoded image
    symptom_extractor_input: Optional[str]  # Specific input for symptom extraction (decided by supervisor)
    symptoms: Dict[str, Any]  # Extracted symptoms from input
    
    # Vision analysis
    image_analysis_result: Dict[str, Any]  # Output from ImageAnalyzerF
        
    # Diagnosis and risk
    diagnosis: Dict[str, Any]  # Output from DiagnosisEngine
    information_needed: Optional[Dict[str, Any]]  # Missing info for accurate diagnosis
    risk_assessment: Dict[str, Any]  # Risk details from DiagnosisEngine
    
    # Revision tracking (to prevent infinite loops)
    revision_count: int  # Number of revision attempts for current diagnosis
    max_revisions: int  # Maximum allowed revisions (default: 2)
    revision_requirements: Optional[str]  # Feedback from DiagnosisCritic
    detailed_review: Optional[str]  # Detailed review from DiagnosisCritic
    
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
    
    plan: List[Dict[str, Any]]  # Added for plan storage
    current_step: int  # Added for tracking current step in the plan
    next_step: Optional[str]  # Added for next step identification

    
