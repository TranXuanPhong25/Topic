"""
Symptom Extractor Agent Node
Extracts and structures symptoms from patient conversations
"""
import json
from typing import Dict, Any, List, Optional
from src.models.state import GraphState
from .config import get_symptom_extractor_model
from .prompts import build_symptom_extraction_prompt


class SymptomExtractorNode:
    """
    Extracts structured symptom information from patient conversations.
    
    This agent:
    - Identifies all mentioned symptoms
    - Standardizes medical terminology
    - Categorizes by body system and severity
    - Detects emergency red flags
    - Extracts timeline and context
    """
    
    def __init__(self, llm_model=None):
        """
        Initialize Symptom Extractor node
        
        Args:
            llm_model: Optional pre-initialized LLM model (for testing)
        """
        self.llm = llm_model or get_symptom_extractor_model()
        print("✅ SymptomExtractorNode initialized")
    
    def __call__(self, state: GraphState) -> GraphState:
        """
        Extract symptoms from user input and conversation history
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with extracted symptoms
        """
        print("\n🩺 === SYMPTOM EXTRACTION STARTED ===")
        
        user_input = state.get("input", "")
        conversation_history = self._build_conversation_history(state)
        
        if not user_input:
            print("⚠️ No user input provided for symptom extraction")
            state["symptoms"] = {
                "error": "No input provided",
                "extracted_symptoms": []
            }
            return state
        
        try:
            # Build extraction prompt
            prompt = build_symptom_extraction_prompt(user_input, conversation_history)
            
            # Generate symptom extraction
            response = self.llm.generate_content(prompt)
            # Parse JSON response
            symptom_data = self._parse_response(response.text)
            
            # # Log extracted information
            self._log_extraction_results(symptom_data)
            #
            # # Check for emergency situations
            if symptom_data.get("requires_emergency_care", False):
                print("🚨 EMERGENCY DETECTED!")
                print(f"   Reason: {symptom_data.get('emergency_reason', 'Unknown')}")
            # Store in state as JSON string for consistency
            state["symptoms"] = symptom_data
            
            print("✅ Symptom extraction completed successfully")
            
        except Exception as e:
            print(f"❌ Error during symptom extraction: {e}")
            # Store error but don't fail the entire pipeline
            state["symptoms"] = {
                "error": str(e),
                "extracted_symptoms": [],
                "raw_input": user_input
            }
        
        return state
    
    def _build_conversation_history(self, state: GraphState) -> str:
        """
        Build conversation history string from state
        
        Args:
            state: Current graph state
            
        Returns:
            Formatted conversation history
        """
        # Check if there's conversation output from previous turns
        conversation_output = state.get("conversation_output", "")
        
        if conversation_output:
            return f"Previous conversation:\n{conversation_output}"
        
        return ""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed symptom data dictionary
        """
        try:
            # Clean response text (remove markdown code blocks if present)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Parse JSON
            symptom_data = json.loads(clean_text)
            
            # Validate required fields
            if "extracted_symptoms" not in symptom_data:
                symptom_data["extracted_symptoms"] = []
            if "red_flags" not in symptom_data:
                symptom_data["red_flags"] = []
            if "requires_emergency_care" not in symptom_data:
                symptom_data["requires_emergency_care"] = False
            
            return symptom_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON response: {e}")
            # Return minimal valid structure
            return {
                "chief_complaint": "Unable to parse",
                "extracted_symptoms": [],
                "red_flags": [],
                "requires_emergency_care": False,
                "error": f"JSON parse error: {str(e)}",
                "raw_response": response_text[:500]  # Store partial raw response
            }
    
    def _log_extraction_results(self, symptom_data: Dict[str, Any]) -> None:
        """
        Log extraction results to console
        
        Args:
            symptom_data: Extracted symptom data
        """
        print("\n📊 Extraction Results:")
        print(f"   Chief Complaint: {symptom_data.get('chief_complaint', 'N/A')}")
        
        symptoms = symptom_data.get("extracted_symptoms", [])
        print(f"   Symptoms Found: {len(symptoms)}")
        for i, symptom in enumerate(symptoms[:3], 1):  # Show first 3
            print(f"      {i}. {symptom.get('symptom', 'Unknown')} ({symptom.get('severity', 'N/A')})")
        
        if len(symptoms) > 3:
            print(f"      ... and {len(symptoms) - 3} more")
        
        red_flags = symptom_data.get("red_flags", [])
        if red_flags:
            print(f"   🚨 Red Flags: {len(red_flags)}")
            for flag in red_flags:
                print(f"      - {flag.get('symptom', 'Unknown')} [{flag.get('urgency_level', 'N/A')}]")
        
        confidence = symptom_data.get("confidence_score", 0)
        print(f"   Confidence Score: {confidence:.2f}")
        
        missing = symptom_data.get("missing_information", [])
        if missing:
            print(f"   ℹ️ Missing Information: {', '.join(missing[:3])}")
    
    def extract_symptoms_directly(self, text: str) -> Dict[str, Any]:
        """
        Direct symptom extraction without state management (for testing/utilities)
        
        Args:
            text: Patient text to extract symptoms from
            
        Returns:
            Extracted symptom data
        """
        try:
            prompt = build_symptom_extraction_prompt(text)
            response = self.llm.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "extracted_symptoms": []
            }
