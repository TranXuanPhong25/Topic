import json
from typing import TYPE_CHECKING

from src.models.state import GraphState


class CombineAnalysisNode:
    """
    CombineAnalysis Node: Merges text symptoms and image analysis.
    """
    
    def __call__(self, state: GraphState) -> GraphState:
        print("🔗 CombineAnalysis: Merging symptoms and image analysis...")
        
        symptoms = state.get("symptoms", "")
        image_analysis = state.get("image_analysis_result", {})
        
        try:
            # Combine information
            visual_desc = image_analysis.get("visual_description", "")
            visual_qa = image_analysis.get("visual_qa_results", {})
            
            combined = f"""**Triệu chứng của bệnh nhân:**
{symptoms}

**Phân tích hình ảnh:**
Mô tả: {visual_desc}

**Kết quả Visual Q&A:**
{json.dumps(visual_qa, ensure_ascii=False, indent=2)}"""
            
            state["combined_analysis"] = combined
            state["messages"].append("✅ CombineAnalysis: Merged successfully")
            
            print(f"Combined analysis length: {len(combined)} characters")
            
        except Exception as e:
            print(f"CombineAnalysis error: {str(e)}")
            state["combined_analysis"] = symptoms  # Fallback to symptoms only
            state["messages"].append(f"❌ CombineAnalysis: Error - {str(e)}")
        
        return state
