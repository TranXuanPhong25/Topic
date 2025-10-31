"""
ConversationAgent Node: Handles normal conversations using clinic information and FAQs.
"""
from typing import TYPE_CHECKING
from .prompts import build_conversation_prompt

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

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
        print("💬 ConversationAgent: Handling conversation...")
        
        user_input = state.get("input", "")
        
        try:
            # Search knowledge base for relevant FAQ
            faq_results = self.knowledge_base.search_faqs(user_input, limit=3)
            
            # Build knowledge base context
            kb_info_parts = [
                f"Clinic: {self.knowledge_base.clinic_info['name']}",
                f"Hours: {self.knowledge_base.clinic_info['hours']}",
                f"Phone: {self.knowledge_base.clinic_info['phone']}"
            ]
            
            # Add relevant FAQs
            for faq in faq_results:
                kb_info_parts.append(f"Q: {faq['question']}\nA: {faq['answer']}")
            
            knowledge_base_info = "\n\n".join(kb_info_parts)
            
            # Build prompt using optimized template
            conversation_prompt = build_conversation_prompt(
                user_input=user_input,
                knowledge_base_info=knowledge_base_info
            )
            
            # Use Gemini to generate response
            response = self.gemini_model.generate_content(conversation_prompt)
            conversation_output = response.text.strip()
            
            state["conversation_output"] = conversation_output
            state["final_response"] = conversation_output
            state["messages"].append("✅ ConversationAgent: Response generated")
            
            print(f"Conversation response: {conversation_output[:100]}...")
            
        except Exception as e:
            print(f"ConversationAgent error: {str(e)}")
            state["conversation_output"] = "Xin lỗi, tôi đang gặp sự cố. Vui lòng gọi phòng khám để được hỗ trợ."
            state["final_response"] = state["conversation_output"]
            state["messages"].append(f"❌ ConversationAgent: Error - {str(e)}")
        
        return state
