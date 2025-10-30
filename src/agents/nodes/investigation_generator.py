"""
InvestigationGenerator Node: Generates potential follow-up tests and investigations.
"""
import json
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class InvestigationGeneratorNode:
    """
    InvestigationGenerator Node: Generates potential follow-up tests.
    """
    
    def __init__(self, gemini_model):
        """
        Initialize the InvestigationGenerator node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
        """
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the investigation generator logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with investigation plan
        """
        print("🔬 InvestigationGenerator: Generating investigation plan...")
        
        diagnosis = state.get("diagnosis", {})
        
        try:
            # Generate investigation plan using Gemini
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

            response = self.gemini_model.generate_content(investigation_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            investigations = json.loads(result_text)
            
            state["investigation_plan"] = investigations
            state["messages"].append(f"✅ InvestigationGenerator: {len(investigations)} tests suggested")
            
            print(f"Generated {len(investigations)} investigation items")
            
        except Exception as e:
            print(f"InvestigationGenerator error: {str(e)}")
            state["investigation_plan"] = []
            state["messages"].append(f"❌ InvestigationGenerator: Error - {str(e)}")
        
        return state
