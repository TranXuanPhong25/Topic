from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots, get_current_datetime
from ..medical_diagnostic_graph import GraphState
from ..utils.message_builder import extract_text_from_gemini_message
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

    def __call__(self, state: "GraphState") -> "GraphState":
        
        user_input = state.get("input", "")
        
        try:
            messages = []
            
            chat_history_raw = state.get("chat_history", [])
            if chat_history_raw:
                for msg in chat_history_raw:
                    role = msg.get("role")
                    text = extract_text_from_gemini_message(msg)
                    
                    if text:
                        if role == "user":
                            messages.append(HumanMessage(content=text))
                        else:
                            messages.append(AIMessage(content=text))
            
            messages.append(HumanMessage(content=user_input))

            result = self.agent.invoke({"messages": messages})
            agent_messages = result.get("messages", [])
            
            print(f"📅 AppointmentScheduler: Processing {len(agent_messages)} messages")
            
            # Find the last AI message (not Tool message) with actual content
            final_response = ""
            from langchain_core.messages import AIMessage as LangChainAIMessage, ToolMessage
            
            for msg in reversed(agent_messages):
                # Skip tool messages (these are tool outputs, not AI responses)
                if isinstance(msg, ToolMessage):
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
            
            # If no valid final response found
            if not final_response:
                # Check if there are tool calls being made
                has_tool_calls = any(
                    hasattr(msg, 'tool_calls') and msg.tool_calls 
                    for msg in agent_messages
                )
                
                if has_tool_calls:
                    # Agent called tools but didn't provide final human-readable response
                    # Extract info from user input and provide a helpful message
                    final_response = "Tôi đã kiểm tra thông tin. Để đặt lịch khám, vui lòng xác nhận: tên bệnh nhân, ngày giờ khám, và lý do khám. Tôi sẽ kiểm tra lịch trống và đặt cho bạn."
                else:
                    final_response = "Tôi sẵn sàng giúp bạn đặt lịch khám. Vui lòng cho tôi biết: ngày giờ bạn muốn, tên đầy đủ, và lý do khám?"
            
            print(f"💬 Final Response: {final_response[:100]}...")
            state["final_response"] = final_response
            state["current_step"] += 1
        except Exception as e:
            print(f"❌ AppointmentScheduler error: {str(e)}")
            import traceback
            traceback.print_exc()
            state["final_response"] = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đặt lịch của bạn. Vui lòng cung cấp thông tin: tên, ngày, giờ, và lý do khám."
        
        return state