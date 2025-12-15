"""Symptom Extractor Agent Node
Extracts and structures symptoms from patient conversations
"""
import json
from typing import Dict, Any, List, Optional
from src.models.state import GraphState
from src.configs.agent_config import SystemMessage, HumanMessage
from src.agents.utils import get_current_context, get_current_goal
from .config import get_symptom_extractor_model
from .prompts import build_symptom_extraction_prompt, SYMPTOM_EXTRACTOR_SYSTEM_PROMPT


class SymptomExtractorNode:
   
    def __init__(self, llm_model=None):
        self.llm = llm_model or get_symptom_extractor_model()
        print("SymptomExtractorNode initialized")
    
    def __call__(self, state: GraphState) -> GraphState:
        print("\n=== SYMPTOM EXTRACTION STARTED ===")
        
        # Check if supervisor specified specific input for extraction
        symptom_extractor_input = state.get("symptom_extractor_input")
        if symptom_extractor_input:
            user_input = symptom_extractor_input
            print(f"Using supervisor-specified input: {user_input[:100]}...")
        else:
            user_input = state.get("input", "")
            print(f"Using default user input: {user_input[:100]}...")
        
        if not user_input:
            print("WARNING: No user input provided for symptom extraction")
            state["symptoms"] = {
                "error": "No input provided",
                "extracted_symptoms": []
            }
            return state
        
        try:
            # Get goal and context from current plan step
            goal = get_current_goal(state)
            context_data = get_current_context(state)
            
            # Build extraction prompt with goal and context
            prompt = build_symptom_extraction_prompt(
                user_input, 
                goal, 
                context_data.get("context", ""), 
                context_data.get("user_context", "")
            )
            
            # Generate symptom extraction
            messages = [
                SystemMessage(content=SYMPTOM_EXTRACTOR_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            # Parse JSON response
            symptom_data = self._parse_response(response.content)
            
            # # Check for emergency situations
            if symptom_data.get("requires_emergency_care", False):
                print("EMERGENCY DETECTED!")
                print(f"   Reason: {symptom_data.get('emergency_reason', 'Unknown')}")
            # Store in state as JSON string for consistency
            state["symptoms"] = symptom_data
            state["current_step"] +=1
            print("Symptom extraction completed successfully")
            
        except Exception as e:
            print(f"ERROR: Error during symptom extraction: {e}")
            # Store error but don't fail the entire pipeline
            state["symptoms"] = {
                "error": str(e),
                "extracted_symptoms": [],
                "raw_input": user_input
            }
        
        return state
    
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
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
            print(f"WARNING: Failed to parse JSON response: {e}")
            # Return minimal valid structure
            return {
                "chief_complaint": "Unable to parse",
                "extracted_symptoms": [],
                "red_flags": [],
                "requires_emergency_care": False,
                "error": f"JSON parse error: {str(e)}",
                "raw_response": response_text[:500]  # Store partial raw response
            }
    