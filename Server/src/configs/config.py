"""Configuration settings for the Medical Clinic Chatbot"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLINIC_CONFIG = {
    "name": "Gemidical",
    "hours": "Mon-Fri 9AM-5PM, Sat 9AM-12PM",
    "phone": "19001836",
    "address": "120 Yên Lãng, Kiến An, Nhật Bản",
    "appointment_duration": 30,  # minutes
    "providers": ["Dr. Phong", "Dr. Đông", "Dr. Mạnh", "Dr. Phước", "Dr. Quang"],
}
