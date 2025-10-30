"""
Recommender Node: Synthesizes investigations and retrieved context to generate final recommendations.
"""
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class RecommenderNode:
    """
    Recommender Node: Synthesizes investigations and retrieved context.
    
    Waits for both InvestigationGenerator and DocumentRetriever to complete.
    """
    
    def __init__(self, gemini_model):
        """
        Initialize the Recommender node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
        """
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the recommender logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with final recommendations
        """
        print("💡 Recommender: Generating final recommendations...")
        
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        investigation_plan = state.get("investigation_plan", [])
        retrieved_documents = state.get("retrieved_documents", [])
        
        try:
            # Build context
            context = f"""**Chẩn đoán:**
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

**Đánh giá rủi ro:**
{json.dumps(risk_assessment, ensure_ascii=False, indent=2)}

**Kế hoạch xét nghiệm:**
{json.dumps(investigation_plan, ensure_ascii=False, indent=2)}

**Tài liệu tham khảo:**
{len(retrieved_documents)} documents retrieved"""
            
            # Generate recommendations using Gemini
            recommendation_prompt = f"""Dựa trên phân tích, đưa ra khuyến nghị cuối cùng cho bệnh nhân.

{context}

**Nhiệm vụ:** Viết khuyến nghị hành động rõ ràng, dễ hiểu (3-5 câu).

Bao gồm:
1. Hành động ngay lập tức (nếu cần)
2. Khi nào cần gặp bác sĩ
3. Xét nghiệm cần làm
4. Chăm sóc tại nhà (nếu phù hợp)

**Khuyến nghị (tiếng Việt, thân thiện):**"""

            response = self.gemini_model.generate_content(recommendation_prompt)
            recommendation = response.text.strip()
            
            state["recommendation"] = recommendation
            state["final_response"] = self._format_final_response(state)
            state["messages"].append("✅ Recommender: Final recommendations generated")
            
            
        except Exception as e:
            print(f"Recommender error: {str(e)}")
            state["recommendation"] = "Vui lòng gặp bác sĩ để được tư vấn chi tiết."
            state["final_response"] = state["recommendation"]
            state["messages"].append(f"❌ Recommender: Error - {str(e)}")
        
        return state
    
    def _format_final_response(self, state: "GraphState") -> str:
        """
        Format the final response for the user.
        
        Args:
            state: Current graph state
            
        Returns:
            Formatted final response string
        """
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        recommendation = state.get("recommendation", "")
        
        response = f"""**🩺 Phân tích y tế:**

**Chẩn đoán sơ bộ:** {diagnosis.get('primary_diagnosis', 'Không xác định')}

**Mức độ rủi ro:** {risk_assessment.get('risk_level', 'MEDIUM')}

{recommendation}

---
*Lưu ý: Đây là phân tích sơ bộ. Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để chẩn đoán chính xác.*"""
        
        return response
