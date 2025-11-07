"""
DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
"""
import json
import re
import requests
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
        print("🩺 DiagnosisEngine: Running diagnostic analysis...")

        # Get input - use combined_analysis if available, otherwise symptoms
        analysis_input = state.get("symptoms", {})
        if analysis_input == {}:
            analysis_input = state.get("input", {})
        print(analysis_input)
        try:
            # Build diagnosis prompt using the system prompt from prompts.py
            image_analysis = json.dumps(state.get("image_analysis_result", ""))
            revision_requirements = state.get("revision_requirements", None)
            detailed_review = state.get("detailed_review", None)
            # Convert analysis_input to string if it's a dict
            symptoms_str = str(analysis_input) if isinstance(analysis_input, dict) else analysis_input
            diagnosis_context = build_diagnosis_prompt(symptoms_str, image_analysis, revision_requirements,
                                                       detailed_review)
            print(diagnosis_context)
            response = self.gemini_model.generate_content(diagnosis_context)
            result_text = response.text.strip()
            diagnosis_context = build_diagnosis_prompt(symptoms_str, image_analysis)

            meditron_text = self._call_meditron(diagnosis_context)
            if meditron_text:
                print("Meditron response received.")
                result_text = meditron_text.strip()
            else:
                response = self.gemini_model.generate_content(diagnosis_context)
                result_text = response.text.strip()

            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            diagnosis = json.loads(result_text)
            # Extract risk assessment from diagnosis
            risk_assessment = diagnosis.get("risk_assessment", {})
            severity = risk_assessment.get("severity", "MODERATE")
            confidence = diagnosis.get("confidence", 0.0)

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

            # Check if we should ask for more information instead of proceeding
            # Only ask on first attempt (not during revisions)
            revision_count = state.get("revision_count", 0)
            if (confidence < 0.6 and
                    revision_count == 0 and
                    information_needed and
                    (information_needed.get("missing_critical_info") or
                     information_needed.get("clarifying_questions"))):
                print(
                    f"💡 DiagnosisEngine: Low confidence ({confidence:.2f}), requesting additional information from user")

                # Note: The final_response should already contain the questions for the user
                # The synthesis/conversation agent will handle sending this to the user

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

    def _call_meditron(self, prompt: str, url: str = "http://127.0.0.1:8080/completion") -> str:
        try:
            payload = {
                "prompt": prompt,
                "n_predict": 256,
                "temperature": 0.2,
                "top_k": 40,
                "top_p": 0.9,
                "stream": False,
            }
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("content") or data.get("text") or resp.text
        except Exception as e:
            print(f"Meditron call failed (diagnosis_engine): {e}")
            return ""
