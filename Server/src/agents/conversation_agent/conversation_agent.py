from typing import TYPE_CHECKING
from .prompts import build_conversation_prompt, CONVERSATION_SYSTEM_PROMPT
from ..utils import build_messages_with_history, get_current_context, get_current_goal
if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class ConversationAgentNode:
    
    def __init__(self, gemini_model, knowledge_base):
        self.gemini_model = gemini_model
        self.knowledge_base = knowledge_base
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("ConversationAgent: Handling conversation...")
        
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
            
            # Get goal and context from current plan step
            goal = get_current_goal(state)
            context_data = get_current_context(state)
            
            conversation_prompt = build_conversation_prompt(
                user_input=user_input,
                knowledge_base_info=knowledge_base_info,
                goal=goal,
                context=context_data.get("context", ""),
                user_context=context_data.get("user_context", "")
            )
            
            messages = build_messages_with_history(
                system_prompt=CONVERSATION_SYSTEM_PROMPT,
                current_prompt=conversation_prompt,
                chat_history=state.get("chat_history", [])
            )
            
            response = self.gemini_model.invoke(messages)
            conversation_output = response.content.strip()
            
            state["final_response"] = conversation_output
            state["current_step"] +=1

            print(f"Conversation response: {conversation_output[:100]}")
            
        except Exception as e:
            print(f"ConversationAgent error: {str(e)}")
            state["final_response"] = "Xin lỗi, tôi đang gặp sự cố. Vui lòng gọi phòng khám để được hỗ trợ."
        
        return state