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
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("==================== InvestigationGenerator ====================")
        
        diagnosis = state.get("diagnosis", {})
        
        try:
            investigation_prompt = f"""Dựa trên chẩn đoán, đề xuất các xét nghiệm/kiểm tra cần thiết.

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
