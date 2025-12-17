from datetime import datetime
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots, get_current_datetime, reschedule_appointment
from src.agents.utils.shared_tools import get_providers_info, get_provider_availability
from ..medical_diagnostic_graph import GraphState
from ..utils.message_builder import build_messages_with_history, extract_text_from_gemini_message, extract_text_from_content
from ..utils import get_current_context, get_current_goal
from src.configs.agent_config import HumanMessage, AIMessage

class AppointmentSchedulerNode:
    
    def __init__(self, model: BaseChatModel):
        # Create React agent with tools
        # The agent will automatically call tools and continue until it provides a final response
        self.agent = create_agent(
            model=model,
            system_prompt=APPOINTMENT_SCHEDULER_SYSTEM_PROMPT,
            tools=[
                get_current_datetime,
                check_appointment_availability,
                book_appointment,
                get_available_time_slots,
                reschedule_appointment,
                get_providers_info,
                get_provider_availability
            ]
        )
    
    async def __call__(self, state: "GraphState") -> "GraphState":
        
        user_input = state.get("input", "")
        intermediate_messages = state.get("intermediate_messages", []) or []
        
        try:
            # Inject current datetime directly into user prompt
            now = datetime.now()
            datetime_context = f"\n[CONTEXT: Current datetime is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%H:%M')} ({now.strftime('%Y-%m-%d %H:%M:%S')})]"
            enriched_user_input = user_input + datetime_context

            messages = build_messages_with_history("", enriched_user_input, state.get("chat_history", []), image_base64=state.get("image"))
            

            result = await self.agent.ainvoke({"messages": messages})
            agent_messages = result.get("messages", [])
            
            print(f"AppointmentScheduler: Processing {len(agent_messages)} messages")
            print("=" * 80)
            
            # Trace all messages and collect intermediate messages for streaming
            from langchain_core.messages import AIMessage as LangChainAIMessage, ToolMessage
            
            for i, msg in enumerate(agent_messages[-5:]):
                msg_type = type(msg).__name__
                print(f"\n[Message {i+1}/{len(agent_messages)}] Type: {msg_type}")
                
                if isinstance(msg, ToolMessage):
                    print(f"  Tool: {msg.name}")
                    print(f"  Output: {msg.content[:200]}..." if len(msg.content) > 200 else f"  Output: {msg.content}")
                    
                elif isinstance(msg, LangChainAIMessage):
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"  AI calling tools: {[tc['name'] for tc in msg.tool_calls]}")
                        for tc in msg.tool_calls:
                            print(f"     - {tc['name']}({tc.get('args', {})})")
                    
                    if hasattr(msg, 'content') and msg.content:
                        # Extract text from content (handles both string and list formats)
                        content_text = extract_text_from_content(msg.content)
                        content_preview = content_text[:150] if len(content_text) > 150 else content_text
                        print(f"  AI Response: {content_preview}...")
                        
                        # Collect intermediate messages (AI responses before tool calls)
                        # These are messages where AI acknowledges and explains what it's doing
                        if hasattr(msg, 'tool_calls') and msg.tool_calls and content_text:
                            # This is an intermediate message - AI is explaining before calling tool
                            intermediate_messages.append(content_text)
                            print(f"  Added intermediate message for streaming")
                    else:
                        print(f"  AI Response: {msg}")
                else:
                    print(f"  Content: {str(msg)[:150]}...")
            
            print("=" * 80)
            
            # Find the last AI message (not Tool message) with actual content
            final_response = ""
            last_tool_output = None
            
            for msg in reversed(agent_messages):
                # Capture the last tool output for fallback response generation
                if isinstance(msg, ToolMessage) and last_tool_output is None:
                    last_tool_output = msg.content
                    continue
                    
                # Look for AI messages with content
                if isinstance(msg, LangChainAIMessage):
                    if hasattr(msg, 'content') and msg.content:
                        # Extract text from content (handles both string and list formats)
                        content = extract_text_from_content(msg.content)
                        if content:
                            # Check if content looks like JSON tool output
                            if not (content.startswith('{') and content.endswith('}')):
                                final_response = content
                                break
            
                    
            # CRITICAL: Detect hallucination - LLM claims booking success without calling book_appointment
            booking_claimed = any(phrase in final_response.lower() for phrase in [
                "đã đặt", "đã cập nhật", "đã hủy", "đã thay đổi", "đã book", 
                "thành công", "đã được cập nhật", "đã được đặt", "đã xác nhận",
                "appointment confirmed", "successfully booked", "has been updated"
            ])
            
            # Check if book_appointment tool was actually called
            tool_called = any(
                isinstance(msg, ToolMessage) and msg.name in ("book_appointment", "check_appointment_availability", "get_available_time_slots")
                for msg in agent_messages
            )
            
            
            if booking_claimed and not tool_called:
                print("WARNING: HALLUCINATION DETECTED: LLM claimed booking success without calling tool!")
                # Override the hallucinated response
                final_response = "Sorry, I encountered an issue processing your booking request"
        
            state["final_response"] = final_response
            state["intermediate_messages"] = intermediate_messages
            state["current_step"] += 1
        except Exception as e:
            print(f"ERROR: AppointmentScheduler error: {str(e)}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "Sorry, I encountered an issue processing your booking request. Please provide: your name, desired date, time, and reason for visit."
            state["intermediate_messages"] = intermediate_messages
        
        return state