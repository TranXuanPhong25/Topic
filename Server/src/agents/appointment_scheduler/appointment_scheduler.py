from datetime import datetime
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots, get_current_datetime
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
                get_available_time_slots
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

            messages = build_messages_with_history("", enriched_user_input, state.get("chat_history", []))
            

            result = await self.agent.ainvoke({"messages": messages})
            agent_messages = result.get("messages", [])
            
            print(f"AppointmentScheduler: Processing {len(agent_messages)} messages")
            print("=" * 80)
            
            # Trace all messages and collect intermediate messages for streaming
            from langchain_core.messages import AIMessage as LangChainAIMessage, ToolMessage
            
            for i, msg in enumerate(agent_messages):
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
            
            # If no valid final response found, generate one based on tool output
            if not final_response:
                print("No valid final response found from agent")
                
                if last_tool_output:
                    print(f"  Using last tool output to generate response: {last_tool_output[:100]}...")
                    # Parse tool output and generate appropriate response
                    try:
                        import json
                        tool_result = json.loads(last_tool_output)
                        
                        # Handle check_appointment_availability response
                        if "available" in tool_result:
                            if tool_result.get("available"):
                                date = tool_result.get("date", "")
                                time = tool_result.get("time", "")
                                final_response = f"Great! The appointment on {date} at {time} is available. To complete the booking, I need to confirm: your full name, reason for visit, and phone number."
                            else:
                                error = tool_result.get("error", "")
                                alternatives = tool_result.get("alternatives", [])
                                if alternatives:
                                    final_response = f"Sorry, {error}. You can choose from these available times: {', '.join(alternatives[:3])}."
                                else:
                                    final_response = f"Sorry, {error}. Please choose a different date or time."
                        
                        # Handle book_appointment response
                        elif "success" in tool_result:
                            if tool_result.get("success"):
                                confirmation = tool_result.get("confirmation", {})
                                final_response = f"Appointment booked successfully!\n\n**Appointment Details:**\n- Name: {confirmation.get('patient_name', 'N/A')}\n- Date: {confirmation.get('date', 'N/A')}\n- Time: {confirmation.get('time', 'N/A')}\n- Reason: {confirmation.get('reason', 'N/A')}\n\nWe will remind you before your visit. Thank you!"
                            else:
                                error = tool_result.get("error", "Không thể đặt lịch")
                                final_response = f"{error}. Vui lòng thử lại hoặc liên hệ phòng khám trực tiếp."
                        
                        # Handle get_available_time_slots response
                        elif "available_slots" in tool_result:
                            slots = tool_result.get("available_slots", [])
                            date = tool_result.get("date", "")
                            if slots:
                                final_response = f"📅 Các khung giờ trống ngày {date}: {', '.join(slots[:5])}. Bạn muốn đặt giờ nào?"
                            else:
                                final_response = f"😔 Không có khung giờ trống ngày {date}. Vui lòng chọn ngày khác."
                        
                        else:
                            final_response = "Tôi đã kiểm tra thông tin. Vui lòng cho tôi biết thêm chi tiết để tiếp tục đặt lịch."
                            
                    except json.JSONDecodeError:
                        final_response = "Tôi đã xử lý yêu cầu của bạn. Vui lòng cho tôi biết nếu cần hỗ trợ thêm."
                else:
                    print("  ℹ️  No tool output available")
                    final_response = "Tôi sẵn sàng giúp bạn đặt lịch khám. Vui lòng cho tôi biết: ngày giờ bạn muốn, tên đầy đủ, và lý do khám?"
            else:
                print(f"Valid final response found: {final_response[:100]}...")
                
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
                    final_response = "Tôi gặp vấn đề khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
            
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