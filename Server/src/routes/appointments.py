from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.handlers.appointment import AppointmentHandler

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# --- PYDANTIC MODELS ---

class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str
    date: str       # Format: "YYYY-MM-DD"
    time: str       # Format: "HH:MM"
    phone: str
    provider: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    patient_name: str
    reason: str
    date: str
    time: str
    phone: str
    provider: str
    status: str

# --- HELPER FUNCTIONS ---

def map_appointment(appointment: dict) -> dict:
    """Chuyển đổi document MongoDB sang dict chuẩn cho API"""
    return {
        "id": appointment.get("id", str(appointment.get("_id", ""))),
        "patient_name": appointment["patient_name"],
        "reason": appointment.get("reason", ""),
        "date": appointment["date"],
        "time": appointment["time"],
        "phone": appointment.get("phone", ""),
        "provider": appointment.get("provider", ""),
        "status": appointment.get("status", "scheduled")
    }


# --- AI FUNCTION (Dành riêng cho Bot/Agent) ---

async def book_appointment_internal(patient_name: str, reason: str, date: str, time: str, phone: str, provider: str = None) -> dict:
    """Internal async function for AI/Agent to book appointments"""
    try:
        handler = AppointmentHandler()
        
        # Validate inputs
        if not patient_name or not date or not time:
            return {"success": False, "message": "Thiếu thông tin bắt buộc (tên, ngày, giờ)."}

        # Use handler's schedule_appointment (async)
        result = await handler.schedule_appointment(
            patient_name=patient_name,
            date=date,
            time=time,
            reason=reason,
            phone=phone,
            provider=provider
        )

        if result["success"]:
            apt = result["appointment"]
            return {
                "success": True,
                "message": f"Đã đặt lịch thành công cho {patient_name} ngày {date} lúc {time}.",
                "data": {
                    "id": apt["id"],
                    "patient_name": patient_name,
                    "date": date,
                    "time": time
                }
            }
        else:
            return {"success": False, "message": result.get("error", "Không thể đặt lịch.")}
            
    except Exception as e:
        print(f"AI Booking Error: {e}")
        return {"success": False, "message": "Lỗi hệ thống khi lưu lịch."}


@router.post("/create", response_model=AppointmentResponse)
async def create_appointment(request: AppointmentRequest):
    """Create a new appointment"""
    handler = AppointmentHandler()
    
    result = await handler.schedule_appointment(
        patient_name=request.patient_name,
        date=request.date,
        time=request.time,
        reason=request.reason,
        phone=request.phone,
        provider=request.provider
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return map_appointment(result["appointment"])


@router.get("/list", response_model=List[AppointmentResponse])
async def list_appointments():
    """List all appointments"""
    handler = AppointmentHandler()
    appointments = await handler.get_appointments()
    return [map_appointment(apt) for apt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    handler = AppointmentHandler()
    appointments = await handler.get_appointments()
    
    # Find the appointment with matching ID
    for apt in appointments:
        if apt.get("id") == appointment_id:
            return map_appointment(apt)
    
    raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám")


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, request: AppointmentRequest):
    """Update an existing appointment"""
    handler = AppointmentHandler()
    
    # First cancel the old appointment
    cancel_result = await handler.cancel_appointment(appointment_id)
    if not cancel_result["success"]:
        raise HTTPException(status_code=404, detail=cancel_result["error"])
    
    # Then create a new one with updated info
    result = await handler.schedule_appointment(
        patient_name=request.patient_name,
        date=request.date,
        time=request.time,
        reason=request.reason,
        phone=request.phone,
        provider=request.provider
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return map_appointment(result["appointment"])


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """Delete/cancel an appointment"""
    handler = AppointmentHandler()
    
    result = await handler.cancel_appointment(appointment_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {"message": result["message"]}