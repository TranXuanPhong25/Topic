"""
ConversationAgent Node: Handles normal conversations using clinic information and FAQs.
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

logger = logging.getLogger(__name__)


class ConversationAgentNode:
    """
    ConversationAgent Node: Handles normal conversations using tools.
    
    Tools: CareGuideTool, FAQTool, ClinicInfoTool, PriceTableTool
    """
    
    def __init__(self, gemini_model, knowledge_base):
        """
        Initialize the ConversationAgent node.
        
        Args:
            gemini_model: Configured Gemini model for text generation
            knowledge_base: FAQ knowledge base for clinic information
        """
        self.gemini_model = gemini_model
        self.knowledge_base = knowledge_base
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the conversation agent logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with conversation output
        """
        logger.info("💬 ConversationAgent: Handling conversation...")
        
        user_input = state.get("input", "")
        
        try:
            # Search knowledge base for relevant FAQ
            faq_results = self.knowledge_base.search_faqs(user_input, limit=3)
            
            # Build context from FAQ
            context = "\n\n".join([
                f"Q: {faq['question']}\nA: {faq['answer']}"
                for faq in faq_results
            ])
            
            # Use Gemini to generate response
            conversation_prompt = f"""Bạn là trợ lý y tế thân thiện cho phòng khám. Trả lời câu hỏi của bệnh nhân.

Thông tin phòng khám:
- Tên: {self.knowledge_base.clinic_info['name']}
- Giờ làm việc: {self.knowledge_base.clinic_info['hours']}
- Điện thoại: {self.knowledge_base.clinic_info['phone']}

Câu hỏi thường gặp liên quan:
{context}

Câu hỏi của bệnh nhân: "{user_input}"

Trả lời ngắn gọn, hữu ích, chuyên nghiệp (2-3 câu):"""

            response = self.gemini_model.generate_content(conversation_prompt)
            conversation_output = response.text.strip()
            
            state["conversation_output"] = conversation_output
            state["final_response"] = conversation_output
            state["messages"].append("✅ ConversationAgent: Response generated")
            
            logger.info(f"Conversation response: {conversation_output[:100]}...")
            
        except Exception as e:
            logger.error(f"ConversationAgent error: {str(e)}")
            state["conversation_output"] = "Xin lỗi, tôi đang gặp sự cố. Vui lòng gọi phòng khám để được hỗ trợ."
            state["final_response"] = state["conversation_output"]
            state["messages"].append(f"❌ ConversationAgent: Error - {str(e)}")
        
        return state
