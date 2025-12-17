"""
Shared Tools
Tools that can be used by multiple agents (appointment_scheduler, conversation_agent, etc.)
"""

from langchain_core.tools import tool
from src.handlers.provider import provider_handler
from typing import Optional


@tool
def get_providers_info(
    specialty: Optional[str] = None,
    day: Optional[str] = None,
    provider_name: Optional[str] = None,
    detailed: bool = False
) -> str:
    """
    Get information about available doctors/providers at the clinic.
    
    Use this tool when patients ask about:
    - Which doctors are available
    - Doctor specialties
    - Doctor schedules
    - Specific doctor information
    - Consultation fees
    
    Args:
        specialty: Filter by medical specialty (e.g., "Dermatologist", "Pediatrician", "General Practitioner")
        day: Filter by day of the week (e.g., "Monday", "Tuesday")
        provider_name: Doctor's title or name (e.g., "Dr. Phong", "Phong", "Dr. Dong", "Dong")
        detailed: If True, return detailed information. If False, return brief summary
    
    Returns:
        Formatted string with provider information
    
    Examples:
        - get_providers_info() -> List all doctors
        - get_providers_info(specialty="Dermatologist") -> List dermatologists
        - get_providers_info(day="Monday") -> List doctors available on Monday
        - get_providers_info(provider_name="Dr. Phong", detailed=True) -> Detailed info about Dr. Phong
        - get_providers_info(provider_name="Phong") -> Info about Dr. Phong (works with just first name)
    
    IMPORTANT: Use doctor's title (e.g., "Dr. Phong") when searching, NOT full name.
    """
    # If specific provider name requested
    if provider_name:
        provider = provider_handler.get_provider_by_name(provider_name)
        if provider:
            return provider_handler.format_provider_info(provider, brief=not detailed)
        else:
            # Suggest using title format
            return f"Doctor '{provider_name}' not found. Try using the doctor's title (e.g., 'Dr. Phong', 'Dr. Dong'). Use get_providers_info() to see all available doctors."
    
    # If specialty filter requested
    if specialty:
        providers = provider_handler.get_providers_by_specialty(specialty)
        if providers:
            result = f"Doctors specialized in {specialty}:\n\n"
            result += provider_handler.format_providers_list(providers, brief=not detailed)
            return result
        else:
            return f"No doctors found with specialty '{specialty}'. Use get_providers_info() to see all available doctors."
    
    # If day filter requested
    if day:
        providers = provider_handler.get_available_providers(day)
        if providers:
            result = f"Doctors available on {day}:\n\n"
            result += provider_handler.format_providers_list(providers, brief=not detailed)
            return result
        else:
            return f"No doctors available on {day}."
    
    # Default: return all providers
    return provider_handler.get_provider_summary()


@tool
def get_provider_availability(provider_name: str) -> str:
    """
    Get the availability schedule for a specific doctor.
    
    Use this tool when patients ask about:
    - When is a specific doctor available?
    - What are the working hours of a doctor?
    - Which days does a doctor work?
    
    Args:
        provider_name: Doctor's title or name (e.g., "Dr. Phong", "Phong", "Dr. Dong", "Dong")
    
    Returns:
        Doctor's availability information
    
    Examples:
        - get_provider_availability("Dr. Phong") -> Returns days and hours Dr. Phong is available
        - get_provider_availability("Phong") -> Works with just first name too
    
    IMPORTANT: Use doctor's title (e.g., "Dr. Phong") when searching, NOT full name.
    """
    provider = provider_handler.get_provider_by_name(provider_name)
    
    if not provider:
        return f"Doctor '{provider_name}' not found. Try using the doctor's title (e.g., 'Dr. Phong', 'Dr. Dong'). Use get_providers_info() to see all available doctors."
    
    available_days = ", ".join(provider.get("available_days", []))
    available_hours = provider.get("available_hours", "N/A")
    
    return (
        f"{provider.get('name')} is available:\n"
        f"  Days: {available_days}\n"
        f"  Hours: {available_hours}\n"
        f"  Specialty: {provider.get('specialty', 'N/A')}"
    )


# Export all shared tools
SHARED_TOOLS = [
    get_providers_info,
    get_provider_availability
]
