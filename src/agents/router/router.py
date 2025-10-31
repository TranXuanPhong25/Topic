"""
Router Node: Classifies user intent and extracts symptoms/image information.
"""
import json
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class RouterNode:
    """
    Router Node: Classifies intent and extracts symptoms/image.
    
    Logic:
    1. Analyze user input
    2. Determine intent (conversation, examiner, symptoms, image+symptoms)
    3. Extract symptoms if present
    4. Extract image if present
    """
    
    def __init__(self, gemini_model):
        """
        Initialize the Router node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
        """
        self.gemini_model = gemini_model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the router node logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with intent and symptoms
        """
        # Check if router has already run (avoid duplicate executions)
        if state.get("intent") and state.get("intent") != "not_classified":
            print("🔀 Router: Already classified, skipping...")
            return state
        
        print("🔀 Router: Classifying user intent...")
        
        user_input = state.get("input", "")
        image = state.get("image")
        
        # Initialize state fields
        state["symptoms"] = ""
        state["intent"] = "normal_conversation"
        state["metadata"] = state.get("metadata", {})
        state["messages"] = state.get("messages", [])
        
        try:
            # Use Gemini to classify intent and extract symptoms
            classification_prompt = f"""Phân tích đầu vào của người dùng và trả về JSON với các trường sau:

Input: "{user_input}"
Có hình ảnh: {"Có" if image else "Không"}

Xác định:
1. intent: "normal_conversation" (hỏi thông tin phòng khám, giá cả, FAQ), 
           "needs_examiner" (muốn đặt lịch khám hoặc cần gặp bác sĩ), 
           "symptoms_only" (mô tả triệu chứng không có hình ảnh), 
           "image_and_symptoms" (có hình ảnh y khoa và triệu chứng)
2. symptoms: chuỗi triệu chứng được trích xuất (nếu có), rỗng nếu không

Chỉ trả về JSON, không có văn bản bổ sung:
{{"intent": "...", "symptoms": "..."}}"""

            response = self.gemini_model.generate_content(classification_prompt)
            result_text = response.text.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            intent = result.get("intent", "normal_conversation")
            symptoms = result.get("symptoms", "")
            
            # Override intent if image is present and symptoms detected
            if image and symptoms:
                intent = "image_and_symptoms"
            elif not image and symptoms:
                intent = "symptoms_only"
            
            state["intent"] = intent
            state["symptoms"] = symptoms
            state["messages"].append(f"✅ Router: Intent classified as '{intent}'")
            
            if symptoms:
                state["messages"].append(f"✅ Router: Extracted symptoms: {symptoms[:100]}...")
            
            print(f"Intent: {intent}, Symptoms: {symptoms[:50]}...")
            
        except Exception as e:
            print(f"Router error: {str(e)}")
            state["intent"] = "normal_conversation"
            state["messages"].append(f"❌ Router: Error - {str(e)}, defaulting to conversation")
        
        return state
