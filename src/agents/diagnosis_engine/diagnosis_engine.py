"""
DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
"""
import json
import re
from typing import Dict, Any, TYPE_CHECKING
from .prompts import build_diagnosis_prompt

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class DiagnosisEngineNode:
    """
    DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
    
    Input: combined_analysis (if image) or symptoms (if symptoms only)
    Internally calls RiskAssessor to refine diagnosis
    """
    
    def __init__(self, gemini_model):
        """
        Initialize the DiagnosisEngine node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
        """
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the diagnosis engine logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with diagnosis and risk assessment
        """
        print("🩺 DiagnosisEngine: Running diagnostic analysis...")
        
        # Get input - use combined_analysis if available, otherwise symptoms
        analysis_input = state.get("combined_analysis") or state.get("symptoms", "")
        
        try:
            # Build diagnosis prompt using the system prompt from prompts.py
            image_analysis = state.get("image_analysis", "")
            # Convert analysis_input to string if it's a dict
            symptoms_str = str(analysis_input) if isinstance(analysis_input, dict) else analysis_input
            diagnosis_context = build_diagnosis_prompt(symptoms_str, image_analysis)
            
            # Generate diagnosis using Gemini with system instruction
            response = self.gemini_model.generate_content(diagnosis_context)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            diagnosis = json.loads(result_text)
            
            # Extract risk assessment from diagnosis
            risk_assessment = diagnosis.get("risk_assessment", {})
            severity = risk_assessment.get("severity", "MODERATE")
            
            # Store diagnosis and risk assessment in state
            state["diagnosis"] = diagnosis
            state["risk_assessment"] = {
                "risk_level": severity,
                "explanation": f"Based on diagnosis: {diagnosis.get('primary_diagnosis', {}).get('condition', 'Unknown')}",
                "red_flags": risk_assessment.get("red_flags", []),
                "complications": risk_assessment.get("complications", []),
                "requires_immediate_attention": severity in ["HIGH", "EMERGENCY"]
            }
            
            # Handle information_needed - store in state for later use
            information_needed = diagnosis.get("information_needed", {})
            if information_needed:
                state["information_needed"] = information_needed
            
            # Store final_response if provided
            if "final_response" in diagnosis:
                state["final_response"] = diagnosis["final_response"]
            
            state["messages"].append(f"✅ DiagnosisEngine: Diagnosis complete (severity: {severity})")
            
            print(f"Diagnosis: {diagnosis.get('primary_diagnosis', {}).get('condition', 'Unknown')}")
            if information_needed.get("clarifying_questions"):
                print(f"Additional info needed: {len(information_needed.get('clarifying_questions', []))} questions")
            
        except Exception as e:
            print(f"DiagnosisEngine error: {str(e)}")
            state["diagnosis"] = {
                "primary_diagnosis": {
                    "condition": "Unable to determine",
                    "probability": 0.0,
                    "reasoning": f"Error: {str(e)}"
                },
                "differential_diagnoses": [],
                "risk_assessment": {
                    "severity": "MODERATE",
                    "red_flags": [],
                    "complications": []
                },
                "confidence": 0.0,
                "information_needed": {},
                "final_response": "Sorry, I encountered an error analyzing your symptoms. Please try again or contact the clinic directly.",
                "recommendation": "Please consult a healthcare professional."
            }
            state["risk_assessment"] = {
                "risk_level": "MEDIUM", 
                "explanation": "Default due to error",
                "requires_immediate_attention": False
            }
            state["messages"].append(f"❌ DiagnosisEngine: Error - {str(e)}")
        
        return state
    
    def _assess_risk_internal(self, severity: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal risk assessor (called by DiagnosisEngine).
        
        Args:
            severity: Severity level from diagnosis
            diagnosis: Full diagnosis dictionary
            
        Returns:
            Risk assessment dictionary
        """
        risk_mapping = {
            "mild": "LOW",
            "moderate": "MEDIUM",
            "severe": "HIGH",
            "critical": "CRITICAL"
        }
        
        risk_level = risk_mapping.get(severity.lower(), "MEDIUM")
        
        # Check for concerning symptoms
        concerning = diagnosis.get("concerning_symptoms", [])
        if len(concerning) >= 3 and risk_level == "MEDIUM":
            risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "explanation": f"Dựa trên mức độ nghiêm trọng: {severity}",
            "requires_immediate_attention": risk_level in ["HIGH", "CRITICAL"]
        }
