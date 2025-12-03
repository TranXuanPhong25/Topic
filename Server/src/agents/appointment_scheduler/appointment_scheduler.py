from datetime import datetime
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots, get_current_datetime
from ..medical_diagnostic_graph import GraphState
from ..utils.message_builder import build_messages_with_history, extract_text_from_gemini_message
from src.configs.agent_config import HumanMessage, AIMessage

class AppointmentSchedulerNode:
    """
    React Agent-based Appointment Scheduler.
    Uses LangGraph's create_react_agent to intelligently handle appointment booking
    by deciding which tools to use based on user input.
    """
    
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
    
    def _get_current_goal(self, state: "GraphState") -> str:
        """
        Extract the goal for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Goal string or empty string if not found
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return ""
        
        current_plan_step = plan[current_step_index]
        goal = current_plan_step.get("goal", "")
        
        if goal:
            print(f"🎯 Current Goal: {goal}")
        
        return goal
    
    def _get_current_context(self, state: "GraphState") -> dict:
        """
        Extract context and user_context for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Dict with 'context' and 'user_context' keys (empty strings if not found)
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return {"context": "", "user_context": ""}
        
        current_plan_step = plan[current_step_index]
        context = current_plan_step.get("context", "")
        user_context = current_plan_step.get("user_context", "")
        
        if context:
            print(f"📝 Context: {context[:100]}...")
        if user_context:
            print(f"👤 User Context: {user_context[:100]}...")
        
        return {"context": context, "user_context": user_context}

    async def __call__(self, state: "GraphState") -> "GraphState":
        
        user_input = state.get("input", "")
        
        try:
            # Inject current datetime directly into user prompt
            now = datetime.now()
            datetime_context = f"\n[CONTEXT: Current datetime is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%H:%M')} ({now.strftime('%Y-%m-%d %H:%M:%S')})]"
            enriched_user_input = user_input + datetime_context

            messages = build_messages_with_history("", enriched_user_input, state.get("chat_history", []))
            

            result = await self.agent.ainvoke({"messages": messages})
            agent_messages = result.get("messages", [])
            
            print(f"📅 AppointmentScheduler: Processing {len(agent_messages)} messages")
            print("=" * 80)
            
            # Trace all messages for debugging
            from langchain_core.messages import AIMessage as LangChainAIMessage, ToolMessage
            
            for i, msg in enumerate(agent_messages):
                msg_type = type(msg).__name__
                print(f"\n[Message {i+1}/{len(agent_messages)}] Type: {msg_type}")
                
                if isinstance(msg, ToolMessage):
                    print(f"  🔧 Tool: {msg.name}")
                    print(f"  📤 Output: {msg.content[:200]}..." if len(msg.content) > 200 else f"  📤 Output: {msg.content}")
                    
                elif isinstance(msg, LangChainAIMessage):
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"  🤖 AI calling tools: {[tc['name'] for tc in msg.tool_calls]}")
                        for tc in msg.tool_calls:
                            print(f"     - {tc['name']}({tc.get('args', {})})")
                    
                    if hasattr(msg, 'content') and msg.content:
                        content_preview = msg.content[:150] if len(msg.content) > 150 else msg.content
                        print(f"  💬 AI Response: {content_preview}...")
                    else:
                        print(f"  💬 AI Response: {msg}")
                else:
                    print(f"  📝 Content: {str(msg)[:150]}...")
            
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
                    if hasattr(msg, 'content') and msg.content and msg.content.strip():
                        # Make sure it's not a tool call response (which might be JSON)
                        content = msg.content.strip()
                        # Check if content looks like JSON tool output
                        if not (content.startswith('{') and content.endswith('}')):
                            final_response = content
                            break
            
            # If no valid final response found, generate one based on tool output
            if not final_response:
                print("⚠️  No valid final response found from agent")
                
                if last_tool_output:
                    print(f"  ℹ️  Using last tool output to generate response: {last_tool_output[:100]}...")
                    # Parse tool output and generate appropriate response
                    try:
                        import json
                        tool_result = json.loads(last_tool_output)
                        
                        # Handle check_appointment_availability response
                        if "available" in tool_result:
                            if tool_result.get("available"):
                                date = tool_result.get("date", "")
                                time = tool_result.get("time", "")
                                final_response = f"✅ Tin tốt! Lịch hẹn vào ngày {date} lúc {time} vẫn còn trống. Để hoàn tất đặt lịch, tôi cần xác nhận thêm: tên đầy đủ của bạn, lý do khám, và số điện thoại liên hệ."
                            else:
                                error = tool_result.get("error", "")
                                alternatives = tool_result.get("alternatives", [])
                                if alternatives:
                                    final_response = f"❌ Xin lỗi, {error}. Bạn có thể chọn các khung giờ trống khác: {', '.join(alternatives[:3])}."
                                else:
                                    final_response = f"❌ Xin lỗi, {error}. Vui lòng chọn ngày hoặc giờ khác."
                        
                        # Handle book_appointment response
                        elif "success" in tool_result:
                            if tool_result.get("success"):
                                confirmation = tool_result.get("confirmation", {})
                                final_response = f"🎉 Đã đặt lịch thành công!\n\n📋 **Chi tiết cuộc hẹn:**\n- Tên: {confirmation.get('patient_name', 'N/A')}\n- Ngày: {confirmation.get('date', 'N/A')}\n- Giờ: {confirmation.get('time', 'N/A')}\n- Lý do: {confirmation.get('reason', 'N/A')}\n\nChúng tôi sẽ liên hệ nhắc nhở trước ngày khám. Cảm ơn bạn!"
                            else:
                                error = tool_result.get("error", "Không thể đặt lịch")
                                final_response = f"❌ {error}. Vui lòng thử lại hoặc liên hệ phòng khám trực tiếp."
                        
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
                print(f"✅ Valid final response found: {final_response[:100]}...")
                
                # CRITICAL: Detect hallucination - LLM claims booking success without calling book_appointment
                booking_claimed = any(phrase in final_response.lower() for phrase in [
                    "đã đặt", "đã cập nhật", "đã hủy", "đã thay đổi", "đã book", 
                    "thành công", "đã được cập nhật", "đã được đặt", "đã xác nhận",
                    "appointment confirmed", "successfully booked", "has been updated"
                ])
                
                # Check if book_appointment tool was actually called
                book_tool_called = any(
                    isinstance(msg, ToolMessage) and msg.name == "book_appointment"
                    for msg in agent_messages
                )
                
                if booking_claimed and not book_tool_called:
                    print("⚠️  HALLUCINATION DETECTED: LLM claimed booking success without calling book_appointment!")
                    # Override the hallucinated response
                    final_response = "Để hoàn tất đặt lịch, tôi cần thực hiện đặt lịch trong hệ thống. Xin vui lòng xác nhận lại thông tin: tên, ngày giờ, lý do khám và số điện thoại để tôi đặt lịch cho bạn."
            
            state["final_response"] = final_response
            state["current_step"] += 1
        except Exception as e:
            print(f"❌ AppointmentScheduler error: {str(e)}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đặt lịch của bạn. Vui lòng cung cấp thông tin: tên, ngày, giờ, và lý do khám."
        
        return state