"""
DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
"""
import json
import re
import requests
from typing import Dict, Any, TYPE_CHECKING

from src.models.state import GraphState
class DiagnosisCriticNode:

    
    def __init__(self, model):

        self.model = model
    
    def __call__(self, state: "GraphState") -> "GraphState":

        print("🩺 DiagnosisEngine: Running diagnostic analysis...")
        
        # Get input - use combined_analysis if available, otherwise symptoms
        symptoms = state.get("symptoms", {})
        analysis_input = state.get("combined_analysis") or json.dumps(symptoms)
        diagnosis = state.get("diagnosis", {})
        try:
            # Generate diagnosis using Gemini
            diagnosis_critic_prompt = self.build_diagnosis_critic_prompt(diagnosis, json.dumps(symptoms.get("extracted_symptoms",state.get("input",""))), state)

            meditron_text = self._call_meditron(diagnosis_critic_prompt)
            if meditron_text:
                result_text = meditron_text.strip()
            else:
                response = self.model.generate_content(diagnosis_critic_prompt)
                result_text = response.text.strip()

            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            try:
                diagnosis = json.loads(result_text)
            except Exception:
                diagnosis = {"error": "Unable to parse diagnosis critic output", "raw": result_text}
            
            print(f"✅ DiagnosisCritic")            
        except Exception as e:
            state["messages"].append(f"❌ DiagnosisCritic: Error - {str(e)}")
        
        return state

    def build_diagnosis_critic_prompt(self, diagnosis: Dict[str, Any], original_symptoms: str, state_context: GraphState) -> str:
        """
        Build diagnosis critic prompt with diagnosis and context
        
        Args:
            diagnosis: Diagnosis results to review
            original_symptoms: Original patient symptoms
            state_context: Additional context from state (optional)
        
        Returns:
            Complete prompt for diagnosis critic
        """
        import json
        
        # Parse symptoms if JSON string
        if isinstance(original_symptoms, str):
            try:
                symptoms_data = json.loads(original_symptoms)
            except:
                symptoms_data = {"raw": original_symptoms}
        else:
            symptoms_data = original_symptoms
        
        context = """Please critically review the following diagnosis assessment and determine if it's ready to proceed or requires revision.

    ## ORIGINAL PATIENT SYMPTOMS
    """
        
        # Add structured symptoms if available
        if isinstance(symptoms_data, dict):
            chief_complaint = symptoms_data.get("chief_complaint", "Not specified")
            context += f"**Chief Complaint**: {chief_complaint}\n\n"
            
            extracted_symptoms = symptoms_data.get("extracted_symptoms", [])
            if extracted_symptoms:
                context += "**Symptoms Reported**:\n"
                for symptom in extracted_symptoms[:8]:  # Top 8 symptoms
                    if isinstance(symptom, dict):
                        context += f"- {symptom.get('symptom', 'Unknown')}: "
                        context += f"{symptom.get('severity', 'N/A')} severity, "
                        context += f"Duration: {symptom.get('duration', 'N/A')}\n"
                    else:
                        context += f"- {symptom}\n"
            
            red_flags_in_symptoms = symptoms_data.get("red_flags", [])
            if red_flags_in_symptoms:
                context += f"\n⚠️ **Red Flags Detected by Symptom Extractor**: {len(red_flags_in_symptoms)}\n"
                for flag in red_flags_in_symptoms:
                    if isinstance(flag, dict):
                        context += f"- {flag.get('symptom', 'Unknown')} [{flag.get('urgency_level', 'unknown')}]\n"
        else:
            context += f"{symptoms_data}\n"
        
        # Add diagnosis to review
        context += "\n## DIAGNOSIS TO REVIEW\n"
        context += f"```json\n{json.dumps(diagnosis, indent=2, ensure_ascii=False)}\n```\n"
        
        # Add any additional context
        if state_context:
            if state_context.get("image_analysis_result"):
                context += "\n## IMAGE ANALYSIS AVAILABLE\n"
                context += "Note: Image analysis was also performed and used in diagnosis.\n"
            
            if state_context.get("combined_analysis"):
                context += "\n## COMBINED ANALYSIS CONTEXT\n"
                context += f"{state_context['combined_analysis']}\n"
        
        # Final instruction
        context += """
    ---

    Using your Chain-of-Thought reasoning process:
    1. Review each quality dimension systematically
    2. Identify strengths and concerns
    3. Make routing decision (supervisor or diagnosis_engine)
    4. Provide specific, actionable feedback if revision is needed

    Output your complete review in the JSON format specified in your system prompt.
    """
        
        return context

    def _call_meditron(self, prompt: str, url: str = "http://127.0.0.1:8080/completion") -> str:
        try:
            payload = {
                "prompt": prompt,
                "n_predict": 512,
                "temperature": 0.2,
                "top_k": 40,
                "top_p": 0.9,
                "stream": False,
            }
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("content") or data.get("text") or resp.text
        except Exception as e:
            print(f"Meditron call failed (diagnosis_critic): {e}")
            return ""
