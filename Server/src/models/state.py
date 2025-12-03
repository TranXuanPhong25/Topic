from typing import Literal, Optional, Dict, TypedDict, Any, List, Annotated, TypeAlias

class GraphState(TypedDict):
    input: str  # Initial user query
    chat_history: Optional[List[Dict[str, Any]]]  # Chat history in Gemini format
    
    # Image and symptoms
    image: Optional[str]  # Base64 encoded image
    image_type: Optional[str]  # Type of image: "medical", "document", "general", "unclear"
    is_diagnostic_image: Optional[bool]  # Whether the image is for diagnostic purposes
    image_analysis_intent: Optional[str]  # User's intent for the image (extracted by analyzer)
    symptom_extractor_input: Optional[str]  # Specific input for symptom extraction (decided by supervisor)
    symptoms: Dict[str, Any]  # Extracted symptoms from input
    
    # Vision analysis
    image_analysis_result: Dict[str, Any]  # Output from ImageAnalyzer
        
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
    rag_answer: Optional[str]  # RAG-generated answer from document retriever
    rag_english_query: Optional[str]  # English query used for RAG retrieval
    document_synthesis: Optional[Dict[str, Any]]  # LLM synthesis of retrieved documents
    
    # Document retrieval tracking
    retriever_caller: Optional[str]  # Agent that called document_retriever (to return after retrieval)
    retriever_query: Optional[str]  # Query sent to document_retriever
    retriever_call_counts: Optional[Dict[str, int]]  # Track how many times each agent called retriever
    max_retriever_calls_per_agent: int  # Maximum retriever calls per agent (default: 2)
    
    # Recommendations
    recommendation: str  # Final actionable advice
        
    # Final output
    final_response: str  # Message to be sent to user
    
    # Streaming support
    intermediate_messages: Optional[List[str]]  # Intermediate messages for streaming (e.g., "checking availability...")
    
    plan: List[Dict[str, Any]]  # Added for plan storage
    current_step: int  # Added for tracking current step in the plan
    next_step: Optional[str]  # Added for next step identification

    
