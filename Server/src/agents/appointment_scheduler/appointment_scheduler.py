from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots, get_current_datetime
from ..medical_diagnostic_graph import GraphState
from src.configs.agent_config import HumanMessage, AIMessage, SystemMessage, BaseMessage

class AppointmentSchedulerNode:
    """
    React Agent-based Appointment Scheduler.
    Uses LangGraph's create_react_agent to intelligently handle appointment booking
    by deciding which tools to use based on user input.
    """
    
    def __init__(self, model: BaseChatModel):
        self.agent = create_agent(
            model=model,
            system_prompt=APPOINTMENT_SCHEDULER_SYSTEM_PROMPT,
            tools=[
                get_current_datetime,
                check_appointment_availability,
                book_appointment,
                get_available_time_slots
            ])
    
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
        """
        Execute appointment scheduling using React Agent.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with appointment details
        """
        print("📅 AppointmentScheduler (React Agent): Processing request...")
        
        user_input = state.get("input", "")
        
        try:
            # Build messages with chat history for full context
            messages = []
            
            # Add chat history as message pairs if available
            chat_history_raw = state.get("chat_history", [])
            if chat_history_raw:
                for msg in chat_history_raw:
                    role = msg.get("role")
                    text_parts = [part.get("text", "") for part in msg.get("parts", [])]
                    text = " ".join(text_parts)
                    
                    if role == "user":
                        messages.append(HumanMessage(content=text))
                    else:  # model/assistant
                        messages.append(AIMessage(content=text))
            
            # Add current user input
            messages.append(HumanMessage(content=user_input))

            # Run the React Agent
            result = self.agent.invoke({"messages": messages})
            print(f"🤖 React Appointment Agent Result: {result}")
            # Extract the final response from agent
            agent_messages = result.get("messages", [])
            final_message = agent_messages[:-1][0]
            print(f"🤖 Final message: {final_message}")
            # Update state
            state["final_response"] = final_message or "I'm ready to help you schedule an appointment. What date and time work for you?"
            state["current_step"] += 1
        except Exception as e:
            print(f"❌ AppointmentScheduler error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            state["final_response"] = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đặt lịch của bạn. Vui lòng cung cấp thông tin: tên, ngày, giờ, và lý do khám."
        
        return state