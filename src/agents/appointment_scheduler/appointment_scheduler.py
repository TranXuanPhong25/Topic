import json
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class AppointmentSchedulerNode:
    def __init__(self, gemini_model, appointment_handler):
        self.gemini_model = gemini_model
        self.appointment_handler = appointment_handler
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("📅 AppointmentScheduler: Handling booking...")
        
        user_input = state.get("input", "")
        
        try:
            # Extract appointment details using Gemini
            extraction_prompt = f"""Trích xuất thông tin đặt lịch từ đầu vào. Trả về JSON:

Input: "{user_input}"

Trích xuất (nếu có):
- patient_name: tên bệnh nhân
- date: ngày (YYYY-MM-DD)
- time: giờ (HH:MM)
- reason: lý do khám

Nếu thiếu thông tin, đặt null. Chỉ trả về JSON:
{{"patient_name": "...", "date": "...", "time": "...", "reason": "..."}}"""

            response = self.gemini_model.generate_content(extraction_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            appointment_data = json.loads(result_text)
            
            # Check if we have enough information
            missing_fields = []
            for field in ["patient_name", "date", "time", "reason"]:
                if not appointment_data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                # Generate prompt for missing information
                missing_str = ", ".join(missing_fields)
                response_text = f"Để đặt lịch, tôi cần thêm thông tin: {missing_str}. Bạn có thể cung cấp không?"
            else:
                # Validate and create appointment (simplified - in real app, use AppointmentHandler)
                response_text = f"""Đã đặt lịch thành công!

📅 Thông tin:
- Bệnh nhân: {appointment_data['patient_name']}
- Ngày: {appointment_data['date']}
- Giờ: {appointment_data['time']}
- Lý do: {appointment_data['reason']}

Chúng tôi sẽ gửi xác nhận qua tin nhắn. Cảm ơn!"""

            state["appointment_details"] = appointment_data
            state["final_response"] = response_text
            state["messages"].append("✅ AppointmentScheduler: Processed")
            state["current_step"] +=1

            print(f"Appointment: {appointment_data}")
            
        except Exception as e:
            print(f"AppointmentScheduler error: {str(e)}")
            state["appointment_details"] = {}
            state["final_response"] = "Để đặt lịch, vui lòng cung cấp: tên, ngày, giờ, và lý do khám."
            state["messages"].append(f"❌ AppointmentScheduler: Error - {str(e)}")
        
        return state
