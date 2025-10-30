"""Configuration settings for the Medical Clinic Chatbot"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLINIC_CONFIG = {
    "name": "Happy Health Clinic",
    "hours": "Mon-Fri 9AM-5PM, Sat 9AM-12PM",
    "phone": "(555) 123-4567",
    "address": "123 Main Street, Anytown, USA",
    "appointment_duration": 30,  # minutes
    "providers": ["Dr. Smith", "Dr. Johnson", "Dr. Williams"],
}
# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinic.db")
