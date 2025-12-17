"""
Provider Handler
Manages provider (doctor) information and availability
"""

from typing import List, Dict, Any, Optional
from src.configs.config import CLINIC_CONFIG


class ProviderHandler:
    """Handler for managing provider information"""
    
    def __init__(self):
        self.providers = CLINIC_CONFIG.get("providers", [])
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of all providers with their information
        
        Returns:
            List of provider dictionaries
        """
        return self.providers
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Get provider information by ID
        
        Args:
            provider_id: The provider's unique ID
            
        Returns:
            Provider dictionary or None if not found
        """
        for provider in self.providers:
            if provider.get("id") == provider_id:
                return provider
        return None
    
    def get_provider_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get provider information by name (case-insensitive)
        Prioritizes matching by title (e.g., "Dr. Phong") over full name
        
        Args:
            name: Provider's name or title (e.g., "Dr. Phong", "Dr. Tran Xuan Phong")
            
        Returns:
            Provider dictionary or None if not found
        """
        name_lower = name.lower()
        
        # First, try to match by title (higher priority)
        for provider in self.providers:
            title = provider.get("title", "").lower()
            if title == name_lower or title in name_lower or name_lower in title:
                return provider
        
        # Then try to match by full name
        for provider in self.providers:
            full_name = provider.get("name", "").lower()
            if full_name == name_lower or full_name in name_lower or name_lower in full_name:
                return provider
        
        return None
    
    def get_providers_by_specialty(self, specialty: str) -> List[Dict[str, Any]]:
        """
        Get providers by specialty
        
        Args:
            specialty: The medical specialty to search for
            
        Returns:
            List of matching providers
        """
        specialty_lower = specialty.lower()
        matching_providers = []
        
        for provider in self.providers:
            specialties = provider.get("specialties", [])
            main_specialty = provider.get("specialty", "")
            
            # Check if specialty matches main specialty or any in the list
            if (main_specialty.lower() == specialty_lower or
                any(s.lower() == specialty_lower for s in specialties)):
                matching_providers.append(provider)
        
        return matching_providers
    
    def get_available_providers(self, day: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get providers available on a specific day
        
        Args:
            day: Day of the week (e.g., "Monday"). If None, returns all providers
            
        Returns:
            List of available providers
        """
        if not day:
            return self.providers
        
        day_capitalized = day.capitalize()
        available_providers = []
        
        for provider in self.providers:
            available_days = provider.get("available_days", [])
            if day_capitalized in available_days:
                available_providers.append(provider)
        
        return available_providers
    
    def format_provider_info(self, provider: Dict[str, Any], brief: bool = False) -> str:
        """
        Format provider information as a readable string
        
        Args:
            provider: Provider dictionary
            brief: If True, return brief info. If False, return detailed info
            
        Returns:
            Formatted string
        """
        if brief:
            return (
                f"{provider.get('name', 'N/A')} - {provider.get('specialty', 'N/A')}\n"
                f"  Available: {', '.join(provider.get('available_days', []))}\n"
                f"  Hours: {provider.get('available_hours', 'N/A')}"
            )
        else:
            specialties_str = ", ".join(provider.get("specialties", []))
            languages_str = ", ".join(provider.get("languages", []))
            
            return (
                f"📋 {provider.get('name', 'N/A')}\n"
                f"   Specialty: {provider.get('specialty', 'N/A')}\n"
                f"   Specialties: {specialties_str}\n"
                f"   Experience: {provider.get('experience', 'N/A')}\n"
                f"   Education: {provider.get('education', 'N/A')}\n"
                f"   Languages: {languages_str}\n"
                f"   Available Days: {', '.join(provider.get('available_days', []))}\n"
                f"   Available Hours: {provider.get('available_hours', 'N/A')}\n"
                f"   Consultation Fee: {provider.get('consultation_fee', 0):,} VND\n"
                f"   Description: {provider.get('description', 'N/A')}"
            )
    
    def format_providers_list(self, providers: List[Dict[str, Any]], brief: bool = True) -> str:
        """
        Format a list of providers as a readable string
        
        Args:
            providers: List of provider dictionaries
            brief: If True, return brief info. If False, return detailed info
            
        Returns:
            Formatted string
        """
        if not providers:
            return "No providers found."
        
        formatted_list = []
        for i, provider in enumerate(providers, 1):
            formatted_list.append(f"{i}. {self.format_provider_info(provider, brief=brief)}")
        
        return "\n\n".join(formatted_list)
    
    def get_provider_summary(self) -> str:
        """
        Get a summary of all providers
        
        Returns:
            Summary string
        """
        summary = f"We have {len(self.providers)} doctors available:\n\n"
        summary += self.format_providers_list(self.providers, brief=True)
        return summary


# Global provider handler instance
provider_handler = ProviderHandler()
