import json

from langchain_core.tools import tool

from src.handlers.appointment import AppointmentHandler


@tool
def check_appointment_availability(date: str, time: str, provider: str | None = None) -> str:
    """
    Check if an appointment slot is available at the specified date and time.

    Args:
        date: Date in YYYY-MM-DD format (e.g., '2025-11-15')
        time: Time in HH:MM format (e.g., '14:00')
        provider: Optional provider name (default: any available)

    Returns:
        JSON string with availability status and details
    """

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

    # Check availability
    available, message = handler.check_availability(date, time, provider)

    if available:
        return json.dumps({
            "available": True,
            "date": date,
            "time": time,
            "provider": provider or "Any available",
            "message": "Slot is available"
        })
    else:
        # Get alternative times
        alternatives = handler.get_available_slots(date, provider)
        return json.dumps({
            "available": False,
            "error": message,
            "alternatives": alternatives[:3],
            "suggestion": f"Try these available times: {', '.join(alternatives[:3])}" if alternatives else "No slots available on this date"
        })


@tool
def book_appointment(
        patient_name: str,
        date: str,
        time: str,
        reason: str,
        phone: str | None = None,
        provider: str | None = None
) -> str:
    """
    Book an appointment for a patient.

    Args:
        patient_name: Full name of the patient
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        reason: Reason for visit
        phone: Patient's phone number (optional)
        provider: Preferred provider name (optional)

    Returns:
        JSON string with booking confirmation or error details
    """

    handler = AppointmentHandler()

    # Use schedule_appointment method which includes all validation
    result = handler.schedule_appointment(
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


@tool
def get_available_time_slots(date: str, limit: int = 5) -> str:
    """
    Get available appointment time slots for a specific date.

    Args:
        date: Date in YYYY-MM-DD format
        limit: Maximum number of slots to return (default: 5)

    Returns:
        JSON string with list of available time slots
    """

    handler = AppointmentHandler()

    # Validate date
    valid_date, date_error = handler.validate_date(date)
    if not valid_date:
        return json.dumps({
            "available_slots": [],
            "error": date_error
        })

    # Get available slots
    all_slots = handler.get_available_slots(date)
    limited_slots = all_slots[:limit]

    return json.dumps({
        "date": date,
        "available_slots": limited_slots,
        "total_found": len(all_slots),
        "showing": len(limited_slots),
        "message": f"Found {len(all_slots)} available slots on {date}, showing {len(limited_slots)}"
    })

