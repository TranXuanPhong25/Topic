from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage

from .prompts import APPOINTMENT_SCHEDULER_SYSTEM_PROMPT
from .tools import check_appointment_availability, book_appointment, get_available_time_slots
from ..medical_diagnostic_graph import GraphState
from src.configs.agent_config import  GEMINI_MODEL_NAME

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
            # Prepare messages for the React Agent
            messages = [HumanMessage(user_input)]

            # Run the React Agent
            print("🤖 React Agent: Analyzing request and selecting tools...")
            result = self.agent.invoke({"messages": messages})

            # Extract the final response from agent
            agent_messages = result.get("messages", [])
            final_message = ""
            
            # Get the last AI message
            for msg in reversed(agent_messages):
                if hasattr(msg, 'content') and msg.content:
                    final_message = msg.content
                    break
            
            # Check if appointment was actually booked by examining tool calls
            appointment_booked = False
            appointment_details = {}
            
            for msg in agent_messages:
                # Check for tool calls in the message
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get('name') == 'book_appointment':
                            # Extract appointment details from tool arguments
                            args = tool_call.get('args', {})
                            appointment_details = {
                                "patient_name": args.get('patient_name'),
                                "date": args.get('date'),
                                "time": args.get('time'),
                                "reason": args.get('reason'),
                                "phone": args.get('phone'),
                                "provider": args.get('provider'),
                                "status": "confirmed"
                            }
                            appointment_booked = True
            
            # Update state
            state["appointment_details"] = appointment_details if appointment_booked else {}
            state["final_response"] = final_message or "I'm ready to help you schedule an appointment. What date and time work for you?"
            state["current_step"] += 1
            
            print(f"📅 Result: {'Appointment booked' if appointment_booked else 'Inquiry handled'}")
            if appointment_booked:
                print(f"   Patient: {appointment_details.get('patient_name')}")
                print(f"   Date/Time: {appointment_details.get('date')} at {appointment_details.get('time')}")
            
        except Exception as e:
            print(f"❌ AppointmentScheduler error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            state["appointment_details"] = {}
            state["final_response"] = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đặt lịch của bạn. Vui lòng cung cấp thông tin: tên, ngày, giờ, và lý do khám."
        
        return state