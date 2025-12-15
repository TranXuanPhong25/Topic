import json
from typing import Dict, Any
from src.models.state import GraphState
from src.configs.agent_config import SystemMessage, HumanMessage
from src.agents.utils import get_current_context, get_current_goal
from .config import get_synthesis_model
from .prompts import build_synthesis_prompt, SYNTHESIS_SYSTEM_PROMPT, COMPACT_SYNTHESIS_PROMPT


class SynthesisNode:
    def __init__(self, llm_model=None):
        self.llm = llm_model or get_synthesis_model()
        print("SynthesisNode initialized")
    
    def __call__(self, state: GraphState) -> GraphState:
        print("\n============= SYNTHESIS STARTED ===========")
        
        try:
            # Gather all available information
            image_analysis_result = state.get("image_analysis_result", {})
            
            # Debug logging for document images
            if image_analysis_result:
                image_type = image_analysis_result.get("image_type", "unknown")
                print(f"Image type: {image_type}")
                if image_type == "document":
                    doc_content = image_analysis_result.get("document_content", "")
                    print(f"Document content length: {len(doc_content)} chars")
                    if doc_content:
                        print(f"Document content preview: {doc_content[:200]}...")
                    else:
                        print("WARNING: No document content in image_analysis_result!")
            
            state_data = {
                "symptoms": state.get("symptoms", ""),
                "image_analysis_result": image_analysis_result,
                "diagnosis": state.get("diagnosis", {}),
                "risk_assessment": state.get("risk_assessment", {}),
                "investigation_plan": state.get("investigation_plan", []),
                "recommendation": state.get("recommendation", ""),
            }
            
            # Get goal and context from current plan step
            goal = get_current_goal(state)
            context_data = get_current_context(state)
            
            # Build synthesis prompt
            synthesis_prompt = build_synthesis_prompt(
                state_data,
                goal=goal,
                context=context_data.get("context", ""),
                user_context=context_data.get("user_context", "")
            )
            # Generate synthesis
            messages = [
                SystemMessage(content=COMPACT_SYNTHESIS_PROMPT),
                HumanMessage(content=synthesis_prompt)
            ]
            response = self.llm.invoke(messages)
            final_report = response.content.strip()

            # Store in state
            state["final_response"] = final_report

            state["current_step"] += 1

        except Exception as e:
            print(f"ERROR during synthesis: {e}")
            # Fallback to basic response
            state["final_response"] = self._create_fallback_response(state)
        
        print("=========== SYNTHESIS ENDED ============\n")
        return state
    
    def _create_fallback_response(self, state: GraphState) -> str:
        """
        Create basic fallback response if synthesis fails
        
        Args:
            state: Current state
            
        Returns:
            Basic formatted response
        """
        print("WARNING: Creating fallback response...")
        
        diagnosis = state.get("diagnosis", {})
        recommendation = state.get("recommendation", "")
        risk_assessment = state.get("risk_assessment", {})
        
        # Build basic response
        response = "## Medical Assessment Summary\n\n"
        
        # Add diagnosis if available
        if diagnosis:
            primary = diagnosis.get("primary_diagnosis", {})
            if isinstance(primary, dict):
                condition = primary.get("condition", "Assessment completed")
                response += f"**Primary Assessment**: {condition}\n\n"
        
        # Add severity
        severity = risk_assessment.get("severity", "MODERATE")
        response += f"**Severity Level**: {severity}\n\n"
        
        # Add recommendations if available
        if recommendation:
            response += "## Recommendations\n\n"
            response += f"{recommendation}\n\n"
        
        # Add standard warning
        response += "---\n\n"
        response += "**Important**: This is a preliminary assessment based on available information. "
        response += "Please consult with a healthcare provider for professional medical advice, "
        response += "diagnosis, and treatment.\n\n"
        
        # Emergency warning if high risk
        if severity in ["HIGH", "EMERGENCY"] or risk_assessment.get("requires_emergency_care"):
            response = "**URGENT MEDICAL ATTENTION MAY BE REQUIRED**\n\n" + response
            response += "\nIf you experience severe symptoms, call 911 or go to the nearest emergency room immediately."
        
        return response
    
    def synthesize_directly(self, state_data: Dict[str, Any]) -> str:
        try:
            # No plan context available in direct synthesis
            prompt = build_synthesis_prompt(state_data, goal="", context="", user_context="")
            messages = [
                SystemMessage(content=COMPACT_SYNTHESIS_PROMPT),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error in synthesis: {str(e)}"