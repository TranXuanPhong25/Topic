"""
DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
"""
import json
import re
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class DiagnosisEngineNode:
    """
    DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
    
    Input: combined_analysis (if image) or symptoms (if symptoms only)
    Internally calls RiskAssessor to refine diagnosis
    """
    
    def __init__(self, gemini_model):
        """
        Initialize the DiagnosisEngine node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
        """
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the diagnosis engine logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with diagnosis and risk assessment
        """
        print("🩺 DiagnosisEngine: Running diagnostic analysis...")
        
        # Get input - use combined_analysis if available, otherwise symptoms
        analysis_input = state.get("combined_analysis") or state.get("symptoms", "")
        
        try:
            # Generate diagnosis using Gemini
            diagnosis_prompt = f"""Bạn là bác sĩ AI chuyên nghiệp. Phân tích thông tin bệnh nhân và đưa ra chẩn đoán sơ bộ.

**Thông tin bệnh nhân:**
{analysis_input}

**Nhiệm vụ:**
1. Đưa ra các chẩn đoán khả năng cao (top 2-3)
2. Mức độ nghiêm trọng
3. Các triệu chứng đáng lo ngại

Trả về JSON:
{{
    "primary_diagnosis": "Chẩn đoán chính",
    "differential_diagnoses": ["Chẩn đoán khác 1", "Chẩn đoán khác 2"],
    "severity": "mild/moderate/severe/critical",
    "concerning_symptoms": ["Triệu chứng 1", "Triệu chứng 2"],
    "explanation": "Giải thích ngắn gọn"
}}

Chỉ trả về JSON:"""

            response = self.gemini_model.generate_content(diagnosis_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            diagnosis = json.loads(result_text)
            
            # Internal risk assessment
            severity = diagnosis.get("severity", "moderate")
            risk_level = self._assess_risk_internal(severity, diagnosis)
            
            state["diagnosis"] = diagnosis
            state["risk_assessment"] = risk_level
            state["messages"].append(f"✅ DiagnosisEngine: Diagnosis complete (severity: {severity})")
            
            print(f"Diagnosis: {diagnosis.get('primary_diagnosis', 'Unknown')}")
            
        except Exception as e:
            print(f"DiagnosisEngine error: {str(e)}")
            state["diagnosis"] = {
                "primary_diagnosis": "Không thể xác định",
                "differential_diagnoses": [],
                "severity": "moderate",
                "concerning_symptoms": [],
                "explanation": f"Lỗi: {str(e)}"
            }
            state["risk_assessment"] = {"risk_level": "MEDIUM", "explanation": "Mặc định do lỗi"}
            state["messages"].append(f"❌ DiagnosisEngine: Error - {str(e)}")
        
        return state
    
    def _assess_risk_internal(self, severity: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal risk assessor (called by DiagnosisEngine).
        
        Args:
            severity: Severity level from diagnosis
            diagnosis: Full diagnosis dictionary
            
        Returns:
            Risk assessment dictionary
        """
        risk_mapping = {
            "mild": "LOW",
            "moderate": "MEDIUM",
            "severe": "HIGH",
            "critical": "CRITICAL"
        }
        
        risk_level = risk_mapping.get(severity.lower(), "MEDIUM")
        
        # Check for concerning symptoms
        concerning = diagnosis.get("concerning_symptoms", [])
        if len(concerning) >= 3 and risk_level == "MEDIUM":
            risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "explanation": f"Dựa trên mức độ nghiêm trọng: {severity}",
            "requires_immediate_attention": risk_level in ["HIGH", "CRITICAL"]
        }
