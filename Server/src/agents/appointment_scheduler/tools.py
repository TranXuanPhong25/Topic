import json
from datetime import datetime

from langchain_core.tools import tool

from src.handlers.appointment import AppointmentHandler
from datetime import timedelta


@tool(description="Get current date and time with examples of relative dates like tomorrow, next week, etc.")
def get_current_datetime() -> str:
    now = datetime.now()
    
    # Calculate common relative dates
    tomorrow = now + timedelta(days=1)
    next_week = now + timedelta(days=7)
    in_3_days = now + timedelta(days=3)
    
    return json.dumps({
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M"),
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "examples": {
            "tomorrow": tomorrow.strftime("%Y-%m-%d"),
            "in_3_days": in_3_days.strftime("%Y-%m-%d"),
            "next_week": next_week.strftime("%Y-%m-%d")
        },
        "message": f"Today is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%H:%M')}"
    })


@tool(description="Check if an appointment slot is available for a specific date, time, and optionally a provider. Returns availability status and alternative times if not available.")
async def check_appointment_availability(date: str, time: str, provider: str | None = None) -> str:
    handler = AppointmentHandler()

    # Validate date
    valid_date, date_error = handler.validate_date(date)
    if not valid_date:
        return json.dumps({
            "available": False,
            "error": date_error,
            "suggestion": "Please choose a different date"
        })

    # Validate time
    valid_time, time_error = handler.validate_time(time)
    if not valid_time:
        return json.dumps({
            "available": False,
            "error": time_error,
            "suggestion": "Please choose a time between 09:00-17:00 on 15-minute intervals"
        })

    # Check availability (async)
    available, message = await handler.check_availability(date, time, provider)

    if available:
        return json.dumps({
            "available": True,
            "date": date,
            "time": time,
            "provider": provider or "Any available",
            "message": "Slot is available"
        })
    else:
        # Get alternative times (async)
        alternatives = await handler.get_available_slots(date, provider)
        return json.dumps({
            "available": False,
            "error": message,
            "alternatives": alternatives[:3],
            "suggestion": f"Try these available times: {', '.join(alternatives[:3])}" if alternatives else "No slots available on this date"
        })


@tool(description="Book an appointment for a patient. Requires patient_name, date (YYYY-MM-DD), time (HH:MM), and reason. Optional: phone and provider.")
async def book_appointment(
        patient_name: str,
        date: str,
        time: str,
        reason: str,
        phone: str | None = None,
        provider: str | None = None
) -> str:
    handler = AppointmentHandler()

    # Use schedule_appointment method which includes all validation (async)
    result = await handler.schedule_appointment(
        patient_name=patient_name,
        date=date,
        time=time,
        reason=reason,
        phone=phone,
        provider=provider
    )

    if result["success"]:
        appointment_data = result.get("appointment", {})
        return json.dumps({
            "success": True,
            "appointment_id": appointment_data.get("id", "PENDING"),
            "confirmation": {
                "patient_name": patient_name,
                "date": date,
                "time": time,
                "reason": reason,
                "provider": appointment_data.get("provider", "Will be assigned"),
                "status": "confirmed"
            },
            "message": result.get("message", f"Appointment successfully booked for {patient_name}")
        })
    else:
        return json.dumps({
            "success": False,
            "error": result.get("error", "Unknown error"),
            "message": "Please try again or contact clinic directly"
        })


@tool(description="Get a list of available appointment time slots for a specific date. Returns up to 'limit' number of slots.")
async def get_available_time_slots(date: str, limit: int = 5) -> str:
    handler = AppointmentHandler()

    # Validate date
    valid_date, date_error = handler.validate_date(date)
    if not valid_date:
        return json.dumps({
            "available_slots": [],
            "error": date_error
        })

    # Get available slots (async)
    all_slots = await handler.get_available_slots(date)
    limited_slots = all_slots[:limit]

    return json.dumps({
        "date": date,
        "available_slots": limited_slots,
        "total_found": len(all_slots),
        "showing": len(limited_slots),
        "message": f"Found {len(all_slots)} available slots on {date}, showing {len(limited_slots)}"
    })