"""DiagnosisEngine Node: Runs core diagnostic logic with risk assessment."""
import json
import re
import requests
from typing import Dict, Any, TYPE_CHECKING
from collections import Counter

from src.models.state import GraphState
from src.configs.agent_config import SystemMessage, HumanMessage
from .prompts import DIAGNOSIS_CRITIC_SYSTEM_PROMPT, DIAGNOSIS_CRITIC_PROMPT

class DiagnosisCriticNode:

    
    def __init__(self, model):

        self.model = model
    
    def _get_current_goal(self, state: "GraphState") -> str:
        """
        Extract the goal for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Goal string or empty string if not found
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return ""
        
        current_plan_step = plan[current_step_index]
        goal = current_plan_step.get("goal", "")
        
        if goal:
            print(f"🎯 Current Goal: {goal}")
        
        return goal
    
    def _get_current_context(self, state: "GraphState") -> Dict[str, str]:
        """
        Extract context and user_context for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Dict with 'context' and 'user_context' keys (empty strings if not found)
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return {"context": "", "user_context": ""}
        
        current_plan_step = plan[current_step_index]
        context = current_plan_step.get("context", "")
        user_context = current_plan_step.get("user_context", "")
        
        if context:
            print(f"📝 Context: {context[:100]}...")
        if user_context:
            print(f"👤 User Context: {user_context[:100]}...")
        
        return {"context": context, "user_context": user_context}
    
    def __call__(self, state: "GraphState") -> "GraphState":

        print("🩺 DiagnosisCritic: Running diagnostic Critic...")        
        # Get input - use combined_analysis if available, otherwise symptoms
        symptoms = state.get("symptoms", {})
        diagnosis = state.get("diagnosis", {})
        try:
            # Determine if we can use fast path review
            severity = diagnosis.get("risk_assessment", {}).get("severity", "MODERATE")
            confidence = diagnosis.get("confidence", 0.0)

            # Fast path for low-risk, high-confidence cases
            if severity == "LOW" and confidence >= 0.7:
                print("⚡ DiagnosisCritic: Using fast path review (low severity, high confidence)")
                fast_review_result = self._fast_review(state, diagnosis)
                # Update state fields individually
                for key, value in fast_review_result.items():
                    state[key] = value  # type: ignore
                return state

            # Full comprehensive review for other cases
            print("🔍 DiagnosisCritic: Using comprehensive review")
            # Generate diagnosis using Gemini

            combined_symptoms = json.dumps(symptoms.get("extracted_symptoms",state.get("input",""))) + json.dumps(state.get("image_analysis_result",""))
            # Generate diagnosis using Gemini
            diagnosis_critic_prompt = self.build_diagnosis_critic_prompt(diagnosis, combined_symptoms, state)
            # TODO: meditron
            meditron_text = None if True else self._call_meditron(diagnosis_critic_prompt)
            if meditron_text:
                print("Meditron response received.")
                result_text = meditron_text.strip()
            else:
                messages = [
                    SystemMessage(content=DIAGNOSIS_CRITIC_SYSTEM_PROMPT),
                    HumanMessage(content=diagnosis_critic_prompt)
                ]
                response = self.model.invoke(messages)
                result_text = response.content.strip()

            result_text = result_text
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            critic_result = json.loads(result_text)
            revision_requirements = critic_result["revision_requirements"]
            routing_decision = critic_result["routing_decision"]
            detailed_review = critic_result["detailed_review"]
            
            state["revision_requirements"] = revision_requirements
            state["detailed_review"] = detailed_review
            
            # Check if revision is needed and if we haven't exceeded max attempts
            requires_revision = routing_decision.get("requires_revision", False)
            revision_count = state.get("revision_count", 0)
            max_revisions = state.get("max_revisions", 2)
            if requires_revision:
                if revision_count >= max_revisions:
                    # Force accept after max attempts to prevent infinite loop
                    state["current_step"] +=1
                    print(f"⚠️ DiagnosisCritic: Max revisions ({max_revisions}) reached. Proceeding despite issues.")
                    state["next_step"] = "supervisor"

                else:
                    # Request revision
                    state["revision_count"] = revision_count + 1
                    state["next_step"] = "diagnosis_engine"
                    print(f"🔄 DiagnosisCritic: Requesting revision (attempt {revision_count + 1}/{max_revisions})")

            else:
                # Diagnosis is acceptable
                state["current_step"] +=1
                state["next_step"] = routing_decision["next_step"]
                print(f"✅ DiagnosisCritic: Diagnosis quality: {critic_result.get('review_summary', {}).get('overall_quality', 'N/A')}")

            print(f"✅ DiagnosisCritic")   
         
        except Exception as e:
            print(f"❌ DiagnosisCritic Error: {str(e)}")
            # On error, proceed to supervisor to avoid blocking
            state["next_step"] = "supervisor"
        return state
    def _fast_review(self, state: "GraphState", diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quick sanity check for low-risk diagnoses.
        Checks basic quality criteria without full LLM review.
        
        Args:
            state: Current graph state
            diagnosis: Diagnosis to review
            
        Returns:
            Updated state fields
        """
        issues = []
        
        # Basic check 1: Has primary diagnosis?
        if not diagnosis.get("primary_diagnosis"):
            issues.append("Missing primary diagnosis")
        
        # Basic check 2: Has at least 2 differential diagnoses?
        diff_diagnoses = diagnosis.get("differential_diagnoses", [])
        if len(diff_diagnoses) < 2:
            issues.append(f"Only {len(diff_diagnoses)} differential diagnoses (need at least 2)")
        
        # Basic check 3: Confidence is reasonable?
        confidence = diagnosis.get("confidence", 0.0)
        if confidence < 0.5:
            issues.append(f"Confidence too low ({confidence}) for low severity case")
        
        # Basic check 4: Has recommendation?
        if not diagnosis.get("recommendation"):
            issues.append("Missing recommendation")
        
        # Basic check 5: No internal contradictions (severity vs red flags)
        risk_assessment = diagnosis.get("risk_assessment", {})
        red_flags = risk_assessment.get("red_flags", [])
        severity = risk_assessment.get("severity", "LOW")
        
        if severity == "LOW" and len(red_flags) > 0:
            issues.append(f"Contradiction: LOW severity but {len(red_flags)} red flags present")
        
        # Decide routing based on issues
        if issues:
            # Has issues - send for revision
            revision_requirements = [
                {
                    "category": "basic_quality",
                    "issue": issue,
                    "suggestion": "Please address this issue",
                    "priority": "HIGH"
                }
                for issue in issues
            ]
            
            return {
                "revision_requirements": json.dumps(revision_requirements),
                "detailed_review": json.dumps({"fast_review": True, "issues": issues}),
                "next_step": "diagnosis_engine",
                "revision_count": state.get("revision_count", 0) + 1,

            }
        else:
            # Passes basic checks - proceed
            return {
                "next_step": "supervisor",

            }
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
            
        # Start building context
        context = "Please critically review the following diagnosis assessment and determine if it is ready to proceed or requires revision.\n\n"
        context += "## ORIGINAL PATIENT SYMPTOMS\n"
        
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

        # Final instruction
        context += "\n---\n\n"
        context += "Using your Chain-of-Thought reasoning process:\n"
        context += "1. Review each quality dimension systematically\n"
        context += "2. Identify strengths and concerns\n"
        context += "3. Make routing decision (supervisor or diagnosis_engine)\n"
        context += "4. Provide specific, actionable feedback if revision is needed\n\n"
        context += "Output your complete review in the JSON format specified in your system prompt.\n"
        
        return context

    def _call_meditron(self, prompt: str, url: str = "http://127.0.0.1:8080/completion") -> str:
        try:
            payload = {
                "prompt": DIAGNOSIS_CRITIC_PROMPT + prompt,
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
            print(f"Meditron call failed (diagnosis_critic): {e}")
            return ""
