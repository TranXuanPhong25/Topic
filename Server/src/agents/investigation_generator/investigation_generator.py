"""InvestigationGenerator Node: Generates potential follow-up tests and investigations."""
import json
import re
from typing import TYPE_CHECKING

from src.configs.agent_config import SystemMessage, HumanMessage
from .prompts import INVESTIGATION_SYSTEM_PROMPT

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class InvestigationGeneratorNode:
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
    
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
    
    def _get_current_context(self, state: "GraphState") -> dict:
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
        print("==================== InvestigationGenerator ====================")
        
        diagnosis = state.get("diagnosis", {})
        
        try:
            # Get goal and context from current plan step
            goal = self._get_current_goal(state)
            context_data = self._get_current_context(state)
            
            # Build investigation prompt with context
            goal_section = f"\n## YOUR GOAL\n{goal}\n" if goal else ""
            context_section = f"\n## CONVERSATION CONTEXT\n{context_data.get('context', '')}\n" if context_data.get('context') else ""
            user_context_section = f"\n## PATIENT'S CONCERNS\n{context_data.get('user_context', '')}\n" if context_data.get('user_context') else ""
            
            investigation_prompt = f"""Dựa trên chẩn đoán, đề xuất các xét nghiệm/kiểm tra cần thiết.
{goal_section}{context_section}{user_context_section}
**Chẩn đoán:**
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

**Nhiệm vụ:** Đề xuất 3-5 xét nghiệm/kiểm tra phù hợp.

Trả về JSON array:
[
    {{"test_name": "Tên xét nghiệm", "reason": "Lý do", "priority": "high/medium/low"}},
    ...
]

Chỉ trả về JSON:"""

            messages = [
                SystemMessage(content=INVESTIGATION_SYSTEM_PROMPT),
                HumanMessage(content=investigation_prompt)
            ]
            response = self.gemini_model.invoke(messages)
            result_text = response.content.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            investigations = json.loads(result_text)
            
            state["investigation_plan"] = investigations
            state["current_step"] += 1
            print(f"Generated {len(investigations)} investigation items:")
            for test_name in investigations:
                print(test_name)
        except Exception as e:
            print(f"InvestigationGenerator error: {str(e)}")
            state["investigation_plan"] = []
        
        return state
