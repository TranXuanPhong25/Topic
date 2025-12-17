from typing import TYPE_CHECKING
from langchain.agents import create_agent
from .prompts import build_conversation_prompt, CONVERSATION_SYSTEM_PROMPT
from src.agents.utils.shared_tools import get_providers_info, get_provider_availability
from ..utils import build_messages_with_history, get_current_context, get_current_goal
from ..utils.message_builder import extract_text_from_gemini_message, extract_text_from_content

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class ConversationAgentNode:
    
    def __init__(self, gemini_model, knowledge_base):
        self.gemini_model = gemini_model
        self.knowledge_base = knowledge_base
        
        # Create React agent with shared tools
        self.agent = create_agent(
            model=gemini_model,
            system_prompt=CONVERSATION_SYSTEM_PROMPT,
            tools=[
                get_providers_info,
                get_provider_availability
            ]
        )
    
    async def __call__(self, state: "GraphState") -> "GraphState":
        print("ConversationAgent: Handling conversation...")
        
        user_input = state.get("input", "")
        intermediate_messages = state.get("intermediate_messages", []) or []
        
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
                system_prompt="",  # System prompt is in agent
                current_prompt=conversation_prompt,
                chat_history=state.get("chat_history", [])
            )
            
            # Use agent instead of direct model call
            result = await self.agent.ainvoke({"messages": messages})
            agent_messages = result.get("messages", [])
            
            print(f"ConversationAgent: Processing {len(agent_messages)} messages")
            print("=" * 80)
            
            # Trace all messages and collect intermediate messages for streaming
            from langchain_core.messages import AIMessage as LangChainAIMessage, ToolMessage
            
            conversation_output = ""
            for msg in agent_messages:
                if isinstance(msg, LangChainAIMessage):
                    content = extract_text_from_content(msg.content)
                    if content:
                        print(f"  AI: {content[:150]}...")
                        conversation_output = content  # Keep last AI message
                        
                        # Add to intermediate messages for streaming
                        # intermediate_messages.append(content)
                            
            print("=" * 80)
            
            state["final_response"] = conversation_output
            state["intermediate_messages"] = intermediate_messages
            state["current_step"] += 1

            print(f"Conversation response: {conversation_output[:100]}")
            
        except Exception as e:
            print(f"ConversationAgent error: {str(e)}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "Sorry, I encountered an issue. Please call the clinic for assistance."
        
        return state