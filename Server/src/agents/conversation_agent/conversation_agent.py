"""
ConversationAgent Node: Handles normal conversations using clinic information and FAQs.
"""
from typing import TYPE_CHECKING
import time
from .prompts import build_conversation_prompt

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class ConversationAgentNode:
    """
    ConversationAgent Node: Handles normal conversations using tools.
    
    Tools: CareGuideTool, FAQTool, ClinicInfoTool, PriceTableTool
    """
    
    def __init__(self, gemini_model, knowledge_base):
        self.gemini_model = gemini_model
        self.knowledge_base = knowledge_base
    
    def __call__(self, state: "GraphState") -> "GraphState":
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
            
            # Use Gemini to generate response with simple backoff on rate limits
            response = self._generate_with_retries(conversation_prompt)
            conversation_output = response.text.strip()
            
            state["conversation_output"] = conversation_output
            state["final_response"] = conversation_output
            state["current_step"] +=1

            print(f"Conversation response: {conversation_output[:100]}...")
            
        except Exception as e:
            print(f"ConversationAgent error: {str(e)}")
            state["conversation_output"] = "Xin lỗi, tôi đang gặp sự cố. Vui lòng gọi phòng khám để được hỗ trợ."
            state["final_response"] = state["conversation_output"]
        
        return state

    def _generate_with_retries(self, prompt: str, retries: int = 3, base_delay: float = 0.75):
        last_err = None
        for attempt in range(retries):
            try:
                return self.gemini_model.generate_content(prompt)
            except Exception as e:
                msg = str(e).lower()
                # naive detection of rate limiting or quota issues
                if "429" in msg or "rate" in msg or "quota" in msg or "exhaust" in msg:
                    delay = base_delay * (2 ** attempt)
                    print(f"⏳ ConversationAgent retry {attempt+1}/{retries} after {delay:.2f}s due to rate limit...")
                    time.sleep(delay)
                    last_err = e
                    continue
                raise
        # If all retries failed
        raise last_err if last_err else RuntimeError("LLM generate failed without exception")
