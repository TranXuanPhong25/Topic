import os
from dotenv import load_dotenv

load_dotenv()

CLINIC_CONFIG = {
    "name": "Gemidical",
    "hours": "Mon-Fri 9AM-5PM, Sat 9AM-12PM",
    "phone": "19001836",
    "address": "120 Yen Lang, Kien An, Hai Hau",
    "appointment_duration": 30,
    "providers": [
        {
            "id": "doctor_001",
            "name": "Dr. Tran Xuan Phong",
            "title": "Dr. Phong",
            "specialty": "General Practitioner",
            "specialties": ["Internal Medicine", "Cardiology", "General Health Checkup"],
            "experience": "8 years",
            "education": "Medical Doctor - Hanoi Medical University",
            "languages": ["Vietnamese", "English"],
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "available_hours": "9:00 - 17:00",
            "consultation_fee": 360000,
            "description": "Experienced doctor in treating internal medicine and cardiovascular diseases. Provides general health consultation."
        },
        {
            "id": "doctor_002", 
            "name": "Dr. Ha Tien Dong",
            "title": "Dr. Dong",
            "specialty": "Dermatologist",
            "specialties": ["Dermatology", "Aesthetic Dermatology", "Acne Treatment"],
            "experience": "6 years",
            "education": "Medical Doctor - Ho Chi Minh City University of Medicine and Pharmacy",
            "languages": ["Vietnamese"],
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "available_hours": "8:30 - 16:30",
            "consultation_fee": 250000,
            "description": "Specialist in dermatological diseases, acne treatment and advanced skin care."
        },
        {
            "id": "doctor_003",
            "name": "Dr. Tran Manh", 
            "title": "Dr. Manh",
            "specialty": "Pediatrician",
            "specialties": ["Pediatrics", "Child Vaccination", "Child Nutrition"],
            "experience": "10 years",
            "education": "Master of Medicine - National Children's Hospital",
            "languages": ["Vietnamese", "English"],
            "available_days": ["Tuesday", "Thursday", "Friday", "Saturday"],
            "available_hours": "9:00 - 16:00",
            "consultation_fee": 300000,
            "description": "Experienced pediatrician specializing in child healthcare and nutrition consultation."
        },
        {
            "id": "doctor_004",
            "name": "Dr. Hoang Phuoc",
            "title": "Dr. Phuoc", 
            "specialty": "ENT Specialist",
            "specialties": ["Otolaryngology", "ENT Surgery", "Endoscopy"],
            "experience": "7 years",
            "education": "Medical Doctor - Hue University of Medicine",
            "languages": ["Vietnamese"],
            "available_days": ["Monday", "Tuesday", "Thursday", "Friday"],
            "available_hours": "8:00 - 17:00",
            "consultation_fee": 280000,
            "description": "ENT specialist with advanced surgical and endoscopic skills."
        },
        {
            "id": "doctor_005",
            "name": "Dr. Do Minh Quang",
            "title": "Dr. Quang",
            "specialty": "Ophthalmologist",
            "specialties": ["Ophthalmology", "Eye Surgery", "Refractive Surgery"],
            "experience": "5 years", 
            "education": "Medical Doctor - Thai Binh Medical University",
            "languages": ["Vietnamese", "English"],
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "available_hours": "9:30 - 17:00",
            "consultation_fee": 270000,
            "description": "Ophthalmologist specializing in eye diseases and refractive surgery."
        }
    ]
}


# Guardrail configuration flags
GUARDRAILS_ENABLED: bool = os.getenv("GUARDRAILS_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
GUARDRAILS_CHECK_OUTPUT: bool = os.getenv("GUARDRAILS_CHECK_OUTPUT", "true").lower() in {"1", "true", "yes", "on"}

