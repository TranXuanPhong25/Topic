"""
Synthesis Agent Node
Synthesizes all diagnostic results into comprehensive final report
"""
import json
from typing import Dict, Any
from src.models.state import GraphState
from src.configs.agent_config import SystemMessage, HumanMessage
from .config import get_synthesis_model
from .prompts import build_synthesis_prompt, SYNTHESIS_SYSTEM_PROMPT


class SynthesisNode:
    """
    Synthesizes all diagnostic information into final comprehensive report.
    
    This agent:
    - Consolidates symptoms, diagnosis, investigations, recommendations
    - Creates clear narrative flow
    - Provides patient-friendly explanations
    - Highlights critical actions and warnings
    - Generates structured final report
    """
    
    def __init__(self, llm_model=None):
        """
        Initialize Synthesis node
        
        Args:
            llm_model: Optional pre-initialized LLM model (for testing)
        """
        self.llm = llm_model or get_synthesis_model()
        print("✅ SynthesisNode initialized")
    
    def _get_current_goal(self, state: GraphState) -> str:
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
    
    def _get_current_context(self, state: GraphState) -> Dict[str, str]:
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
    
    def __call__(self, state: GraphState) -> GraphState:
        print("\n📊 ============= SYNTHESIS STARTED ===========")
        
        try:
            # Gather all available information
            state_data = {
                "symptoms": state.get("symptoms", ""),
                "image_analysis_result": state.get("image_analysis_result", {}),
                "diagnosis": state.get("diagnosis", {}),
                "risk_assessment": state.get("risk_assessment", {}),
                "investigation_plan": state.get("investigation_plan", []),
                "recommendation": state.get("recommendation", ""),
            }
            
            # Get goal and context from current plan step
            goal = self._get_current_goal(state)
            context_data = self._get_current_context(state)
            
            # Build synthesis prompt
            synthesis_prompt = build_synthesis_prompt(
                state_data,
                goal=goal,
                context=context_data.get("context", ""),
                user_context=context_data.get("user_context", "")
            )
            # Generate synthesis
            messages = [
                SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
                HumanMessage(content=synthesis_prompt)
            ]
            response = self.llm.invoke(messages)
            final_report = response.content.strip()
            
            # Log report sections
            self._log_synthesis_results(final_report)
            
            # Store in state
            state["final_response"] = final_report

            # Check for emergency indicators in report
            if "🚨" in final_report or "URGENT" in final_report.upper():
                print("🚨 EMERGENCY INDICATORS DETECTED IN FINAL REPORT")
            state["current_step"] += 1

        except Exception as e:
            print(f"❌ Error during synthesis: {e}")
            # Fallback to basic response
            state["final_response"] = self._create_fallback_response(state)
        
        print("📊 =========== SYNTHESIS ENDED ============\n")
        return state
    
    def _log_synthesis_results(self, report: str) -> None:
        """
        Log synthesis results to console
        
        Args:
            report: Generated final report
        """
        lines = report.split('\n')
        print("\n📋 Final Report Preview:")
        print(f"   Total Length: {len(report)} characters")
        print(f"   Lines: {len(lines)}")
        
        # Show first few lines
        preview_lines = min(5, len(lines))
        for i in range(preview_lines):
            if lines[i].strip():
                preview = lines[i][:80] + "..." if len(lines[i]) > 80 else lines[i]
                print(f"   {preview}")
        
        if len(lines) > preview_lines:
            print(f"   ... and {len(lines) - preview_lines} more lines")
        
        # Check for key sections
        sections = []
        if "Summary" in report or "Overview" in report:
            sections.append("Summary")
        if "Symptoms" in report:
            sections.append("Symptoms")
        if "Diagnosis" in report or "Assessment" in report:
            sections.append("Diagnosis")
        if "Investigation" in report or "Tests" in report:
            sections.append("Investigations")
        if "Treatment" in report or "Recommendation" in report:
            sections.append("Recommendations")
        if "Warning" in report or "Emergency" in report:
            sections.append("Warnings")
        
        if sections:
            print(f"   Sections Included: {', '.join(sections)}")
    
    def _create_fallback_response(self, state: GraphState) -> str:
        """
        Create basic fallback response if synthesis fails
        
        Args:
            state: Current state
            
        Returns:
            Basic formatted response
        """
        print("⚠️ Creating fallback response...")
        
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
        response += "⚠️ **Important**: This is a preliminary assessment based on available information. "
        response += "Please consult with a healthcare provider for professional medical advice, "
        response += "diagnosis, and treatment.\n\n"
        
        # Emergency warning if high risk
        if severity in ["HIGH", "EMERGENCY"] or risk_assessment.get("requires_emergency_care"):
            response = "🚨 **URGENT MEDICAL ATTENTION MAY BE REQUIRED**\n\n" + response
            response += "\n🚨 If you experience severe symptoms, call 911 or go to the nearest emergency room immediately."
        
        return response
    
    def synthesize_directly(self, state_data: Dict[str, Any]) -> str:
        try:
            # No plan context available in direct synthesis
            prompt = build_synthesis_prompt(state_data, goal="", context="", user_context="")
            messages = [
                SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error in synthesis: {str(e)}"