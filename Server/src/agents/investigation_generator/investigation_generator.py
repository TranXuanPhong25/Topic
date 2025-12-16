import json
import re
from typing import TYPE_CHECKING

from src.configs.agent_config import SystemMessage, HumanMessage
from src.agents.utils import get_current_context, get_current_goal
from .prompts import INVESTIGATION_SYSTEM_PROMPT

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class InvestigationGeneratorNode:
    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("==================== InvestigationGenerator ====================")
        
        diagnosis = state.get("diagnosis", {})
        
        try:
            # Get goal and context from current plan step
            goal = get_current_goal(state)
            context_data = get_current_context(state)
            
            # Build investigation prompt with context
            goal_section = f"\n## YOUR GOAL\n{goal}\n" if goal else ""
            context_section = f"\n## CONVERSATION CONTEXT\n{context_data.get('context', '')}\n" if context_data.get('context') else ""
            user_context_section = f"\n## PATIENT'S CONCERNS\n{context_data.get('user_context', '')}\n" if context_data.get('user_context') else ""
            
            investigation_prompt = f"""Based on the diagnosis, suggest necessary tests and investigations.
{goal_section}{context_section}{user_context_section}
**Diagnosis:**
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

**Task:** Suggest 3-5 appropriate tests/investigations.

Return JSON array:
[
    {{"test_name": "Test name", "reason": "Reason", "priority": "high/medium/low"}},
    ...
]

Return only JSON:"""
            messages = [
                SystemMessage(content=INVESTIGATION_SYSTEM_PROMPT),
                HumanMessage(content=investigation_prompt)
            ]
            response = self.gemini_model.invoke(messages)
            result_text = response.content.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            investigations = json.loads(result_text)
            if state["final_response"] is None:
                state["final_response"] = investigations
            state["investigation_plan"] = investigations
            state["current_step"] += 1
            for test_name in investigations:
                print(test_name)
        except Exception as e:
            print(f"InvestigationGenerator error: {str(e)}")
            state["investigation_plan"] = []
        
        return state
