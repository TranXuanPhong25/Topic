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

def map_appointment(appointment: dict) -> dict:
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

@router.post("/create", response_model=AppointmentResponse)
async def create_appointment(request: AppointmentRequest):
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
    handler = AppointmentHandler()
    appointments = await handler.get_appointments()
    return [map_appointment(apt) for apt in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    handler = AppointmentHandler()
    appointments = await handler.get_appointments()
    
    # Find the appointment with matching ID
    for apt in appointments:
        if apt.get("id") == appointment_id:
            return map_appointment(apt)
    
    raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám")


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, request: AppointmentRequest):
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
    handler = AppointmentHandler()
    
    result = await handler.cancel_appointment(appointment_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {"message": result["message"]}