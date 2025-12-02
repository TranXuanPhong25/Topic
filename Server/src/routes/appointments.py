from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from bson import ObjectId
from src.database import get_collection 
import traceback

router = APIRouter(prefix="/appointments", tags=["Appointments"])
collection = get_collection("appointments")

# --- PYDANTIC MODELS ---

class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str
    time: str      # Format: "YYYY-MM-DD HH:MM"
    phone: str

class AppointmentResponse(AppointmentRequest):
    id: str        # Trả về ID dạng string cho Frontend dễ dùng

# --- HELPER FUNCTIONS ---

def map_appointment(appointment: dict) -> dict:
    """Chuyển đổi document MongoDB sang dict chuẩn cho API (đổi _id -> id)"""
    return {
        "id": str(appointment["_id"]),
        "patient_name": appointment["patient_name"],
        "reason": appointment["reason"],
        "time": appointment["time"],
        "phone": appointment.get("phone", "")
    }

async def is_duplicate_time(time_str: str, ignore_id_str: str = "") -> bool:
    """Kiểm tra trùng lịch (có hỗ trợ loại trừ ID khi update)"""
    query :Dict[str, Any]= {"time": time_str}
    
    if ignore_id_str:
        try:
            # Loại trừ chính document đang sửa
            query["_id"] = {"$ne": ObjectId(ignore_id_str)}
        except Exception:
            pass # Nếu ID không hợp lệ thì bỏ qua filter này

    existing_appointment = await collection.find_one(query)
    return existing_appointment is not None

# --- AI FUNCTION (Dành riêng cho Bot/Agent) ---

async def book_appointment_internal(patient_name: str, reason: str, time: str, phone: str) -> dict:
    try:
        # 1. Validate
        if not time or not patient_name:
            return {"success": False, "message": "Thiếu tên hoặc thời gian."}

        # 2. Check trùng
        if await is_duplicate_time(time):
            return {"success": False, "message": f"Giờ {time} đã có người đặt."}

        # 3. Insert
        new_data = {
            "patient_name": patient_name,
            "reason": reason,
            "time": time,
            "phone": phone
        }
        result = await collection.insert_one(new_data)

        return {
            "success": True,
            "message": f"Đã đặt lịch thành công cho {patient_name} lúc {time}.",
            "data": {
                "id": str(result.inserted_id),
                "patient_name": patient_name,
                "time": time
            }
        }
    except Exception as e:
        print(f"AI Booking Error: {e}")
        return {"success": False, "message": "Lỗi hệ thống khi lưu lịch."}


@router.post("/create", response_model=AppointmentResponse)
async def create_appointment(request: AppointmentRequest):
    # 1. Kiểm tra trùng giờ
    if await is_duplicate_time(request.time):
        raise HTTPException(
            status_code=400,
            detail=f"Đã có lịch khám lúc {request.time}. Vui lòng chọn thời gian khác."
        )

    # 2. Tạo dữ liệu (Chuyển Pydantic -> Dict)
    new_appointment_dict = request.model_dump()

    result = await collection.insert_one(new_appointment_dict)

    # 4. Gán lại _id vừa sinh ra để map dữ liệu trả về
    new_appointment_dict["_id"] = result.inserted_id

    return map_appointment(new_appointment_dict)


@router.get("/list", response_model=List[AppointmentResponse])
async def list_appointments():
    appointments = []
    # Lấy tất cả, không cần {"_id": 0} nữa vì ta cần lấy ID
    cursor = collection.find()
    
    async for document in cursor:
        appointments.append(map_appointment(document))

    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str):
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    appointment = await collection.find_one({"_id": oid})

    if not appointment:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám")
    
    return map_appointment(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(appointment_id: str, request: AppointmentRequest):
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    # 1. Kiểm tra tồn tại
    existing_ppt = await collection.find_one({"_id": oid})
    if not existing_ppt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám")

    # 2. Kiểm tra trùng giờ (trừ chính ID này)
    if await is_duplicate_time(request.time, ignore_id_str=appointment_id):
        raise HTTPException(
            status_code=400,
            detail=f"Đã có lịch khám lúc {request.time}. Vui lòng chọn thời gian khác."
        )

    # 3. Thực hiện update
    update_data = request.dict()
    
    await collection.update_one(
        {"_id": oid},
        {"$set": update_data}
    )

    # Trả về dữ liệu mới (kèm ID cũ)
    update_data["_id"] = oid
    return map_appointment(update_data)


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    try:
        oid = ObjectId(appointment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    result = await collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám")

    return {"message": "Đã xóa lịch khám thành công"}