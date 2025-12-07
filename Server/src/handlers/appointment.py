"""Appointment scheduling handler with validation"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId

from src.database import get_collection
from src.configs.config import CLINIC_CONFIG


class AppointmentHandler:
    """
    Handles appointment scheduling with validation.
    Includes date/time validation, business hours checking, and database persistence.
    """
    
    def __init__(self):
        self.clinic_hours_start = "09:00"
        self.clinic_hours_end = "17:00"
        self.appointment_duration = CLINIC_CONFIG.get("appointment_duration", 30)
        self.providers = CLINIC_CONFIG.get("providers", [])
        self.collection = get_collection("appointments")
    
    def validate_date(self, date_str: str) -> tuple[bool, str]:
        """
        Validate appointment date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Parse date
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if date is in the past
            if date.date() < datetime.now().date():
                return False, "Cannot schedule appointments in the past"
            
            # Check if date is too far in the future (6 months)
            max_future = datetime.now() + timedelta(days=180)
            if date.date() > max_future.date():
                return False, "Cannot schedule appointments more than 6 months in advance"
            
            # Check if it's a weekend (Saturday=5, Sunday=6)
            if date.weekday() == 6:  # Sunday
                return False, "Clinic is closed on Sundays"
            
            return True, ""
            
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD"
    
    def validate_time(self, time_str: str) -> tuple[bool, str]:
        """
        Validate appointment time.
        
        Args:
            time_str: Time in HH:MM format (24-hour)
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Parse time
            time = datetime.strptime(time_str, "%H:%M").time()
            
            # Parse clinic hours
            start_time = datetime.strptime(self.clinic_hours_start, "%H:%M").time()
            end_time = datetime.strptime(self.clinic_hours_end, "%H:%M").time()
            
            # Check if within business hours
            if time < start_time or time >= end_time:
                return False, f"Appointments available {self.clinic_hours_start} to {self.clinic_hours_end}"
            
            # Check if time is on 15-minute intervals
            if time.minute not in [0, 15, 30, 45]:
                return False, "Appointments must be on 15-minute intervals (e.g., 9:00, 9:15, 9:30)"
            
            return True, ""
            
        except ValueError:
            return False, "Invalid time format. Please use HH:MM (e.g., 14:00 for 2 PM)"
    
    def validate_provider(self, provider: Optional[str]) -> tuple[bool, str]:
        """Validate provider name"""
        if provider and provider not in self.providers:
            return False, f"Provider not found. Available: {', '.join(self.providers)}"
        return True, ""
    
    async def check_availability(self, date: str, time: str, provider: Optional[str] = None) -> tuple[bool, str]:
        """
        Check if appointment slot is available.
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            provider: Optional provider name
            
        Returns:
            (is_available, message)
        """
        query = {
            "date": date,
            "time": time,
            "status": "scheduled"
        }
        
        if provider:
            query["provider"] = provider
        
        existing = await self.collection.find_one(query)
        
        if existing:
            if provider:
                return False, f"{provider} is not available at that time"
            else:
                return False, "That time slot is already booked"
        
        return True, ""
    
    async def schedule_appointment(
        self,
        patient_name: str,
        date: str,
        time: str,
        reason: str,
        provider: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a new appointment with full validation.
        
        Args:
            patient_name: Patient's full name
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            reason: Reason for visit
            provider: Optional provider name
            phone: Optional phone number
            email: Optional email address
            
        Returns:
            Dictionary with success status, appointment data, or error
        """
        # Validate date
        valid, error = self.validate_date(date)
        if not valid:
            return {"success": False, "error": error}
        
        # Validate time
        valid, error = self.validate_time(time)
        if not valid:
            return {"success": False, "error": error}
        
        # Validate provider
        if provider:
            valid, error = self.validate_provider(provider)
            if not valid:
                return {"success": False, "error": error}
        
        # Check availability (async)
        available, error = await self.check_availability(date, time, provider)
        if not available:
            return {"success": False, "error": error}
        
        # Create appointment document
        try:
            now = datetime.utcnow()
            appointment_doc = {
                "patient_name": patient_name,
                "date": date,
                "time": time,
                "reason": reason,
                "provider": provider or self.providers[0],  # Default to first provider
                "phone": phone or "",
                "email": email or "",
                "status": "scheduled",
                "notes": "",
                "created_at": now,
                "updated_at": now
            }
            
            result = await self.collection.insert_one(appointment_doc)
            appointment_id = str(result.inserted_id)
            
            message = f"Appointment scheduled for {patient_name} on {date} at {time}"
            
            # Prepare appointment data for response
            appointment_data = {
                "id": appointment_id,
                **appointment_doc,
                "created_at": appointment_doc["created_at"].isoformat(),
                "updated_at": appointment_doc["updated_at"].isoformat()
            }
            
            return {
                "success": True,
                "appointment": appointment_data,
                "message": message,
            }
                
        except Exception as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    async def get_appointments(
        self,
        patient_name: Optional[str] = None,
        date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve appointments with optional filters.
        
        Args:
            patient_name: Filter by patient name
            date: Filter by date (YYYY-MM-DD)
            status: Filter by status
            
        Returns:
            List of appointment dictionaries
        """
        query: Dict[str, Any] = {}
        
        if patient_name:
            query["patient_name"] = {"$regex": patient_name, "$options": "i"}
        if date:
            query["date"] = date
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort([("date", 1), ("time", 1)])
        appointments = []
        
        async for doc in cursor:
            appointment_data = {
                "id": str(doc["_id"]),
                "patient_name": doc["patient_name"],
                "date": doc["date"],
                "time": doc["time"],
                "reason": doc.get("reason", ""),
                "provider": doc.get("provider", ""),
                "status": doc["status"],
                "phone": doc.get("phone", ""),
                "email": doc.get("email", ""),
                "notes": doc.get("notes", ""),
                "created_at": doc["created_at"].isoformat(),
                "updated_at": doc["updated_at"].isoformat(),
            }
            appointments.append(appointment_data)
        
        return appointments
    
    async def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: ID of appointment to cancel (MongoDB ObjectId as string)
            
        Returns:
            Success status and message
        """
        try:
            # Convert string ID to ObjectId
            try:
                obj_id = ObjectId(appointment_id)
            except:
                return {"success": False, "error": "Invalid appointment ID"}
            
            appointment = await self.collection.find_one({"_id": obj_id})
            
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            if appointment.get("status") == "cancelled":
                return {"success": False, "error": "Appointment already cancelled"}
            
            # Update status to cancelled
            await self.collection.update_one(
                {"_id": obj_id},
                {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
            )
            
            return {
                "success": True,
                "message": f"Appointment for {appointment['patient_name']} cancelled"
            }
                
        except Exception as e:
            return {"success": False, "error": f"Error cancelling appointment: {str(e)}"}
    
    async def get_available_slots(self, date: str, provider: Optional[str] = None) -> List[str]:
        """
        Get available appointment slots for a given date.
        
        Args:
            date: Date in YYYY-MM-DD format
            provider: Optional provider to check availability for
            
        Returns:
            List of available time slots
        """
        # Generate all possible slots (15-minute intervals)
        start = datetime.strptime(self.clinic_hours_start, "%H:%M")
        end = datetime.strptime(self.clinic_hours_end, "%H:%M")
        
        all_slots = []
        current = start
        while current < end:
            all_slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=15)
        
        # Get booked slots
        query = {
            "date": date,
            "status": "scheduled"
        }
        
        if provider:
            query["provider"] = provider
        
        cursor = self.collection.find(query)
        booked_times = set()
        
        async for doc in cursor:
            booked_times.add(doc["time"])
        
        # Return available slots
        return [slot for slot in all_slots if slot not in booked_times]


# Global appointment handler instance
appointment_handler = AppointmentHandler()


# Function calling schema for Gemini
SCHEDULE_APPOINTMENT_DECLARATION = {
    "name": "schedule_appointment",
    "description": "Schedule a new appointment for a patient. Collects patient information and desired date/time.",
    "parameters": {
        "type": "object",
        "properties": {
            "patient_name": {
                "type": "string",
                "description": "Patient's full name"
            },
            "date": {
                "type": "string",
                "description": "Appointment date in YYYY-MM-DD format"
            },
            "time": {
                "type": "string",
                "description": "Appointment time in HH:MM format (24-hour, e.g., 14:00 for 2 PM)"
            },
            "reason": {
                "type": "string",
                "description": "Reason for visit (e.g., checkup, flu symptoms, follow-up)"
            },
            "phone": {
                "type": "string",
                "description": "Patient's phone number (optional)"
            },
            "provider": {
                "type": "string",
                "description": f"Preferred provider: {', '.join(CLINIC_CONFIG['providers'])} (optional)"
            }
        },
        "required": ["patient_name", "date", "time", "reason"]
    }
}


async def schedule_appointment_function(patient_name: str, date: str, time: str, reason: str,
                                  phone: str = "", provider: str = "") -> str:
    """
    Function that Gemini can call to schedule appointments.
    Returns a string response to be shown to the user.
    """
    result = await appointment_handler.schedule_appointment(
        patient_name=patient_name,
        date=date,
        time=time,
        reason=reason,
        phone=phone,
        provider=provider
    )
    
    if result["success"]:
        apt = result["appointment"]
        return f"✅ Appointment confirmed!\n\nPatient: {apt['patient_name']}\nDate: {apt['date']}\nTime: {apt['time']}\nProvider: {apt['provider']}\nReason: {apt['reason']}\n\nWe'll send a reminder before your appointment."
    else:
        return f"❌ Unable to schedule: {result['error']}\n\nPlease try a different date or time."
