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
    "doctors": [
        {
            "id": "doctor_001",
            "name": "Bác sĩ Trần Xuân Phong",
            "title": "Dr. Phong",
            "specialty": "Bác sĩ đa khoa",
            "specialties": ["Nội khoa", "Tim mạch", "Khám sức khỏe tổng quát"],
            "experience": "8 năm",
            "education": "Bác sĩ Y khoa - ĐH Y Hà Nội",
            "languages": ["Tiếng Việt", "English"],
            "available_days": ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"],
            "available_hours": "9:00 - 17:00",
            "consultation_fee": 360000,  # VND
            "description": "Bác sĩ có kinh nghiệm trong điều trị các bệnh nội khoa và tim mạch. Tư vấn khám sức khỏe tổng quát."
        },
        {
            "id": "doctor_002", 
            "name": "Bác sĩ Nguyễn Văn Đông",
            "title": "Dr. Đông",
            "specialty": "Bác sĩ Da liễu",
            "specialties": ["Da liễu", "Thẩm mỹ da", "Điều trị mụn"],
            "experience": "6 năm",
            "education": "Bác sĩ Y khoa - ĐH Y dược TP.HCM",
            "languages": ["Tiếng Việt"],
            "available_days": ["Thứ 2", "Thứ 4", "Thứ 6", "Thứ 7"],
            "available_hours": "8:30 - 16:30",
            "consultation_fee": 250000,  # VND
            "description": "Chuyên gia về các bệnh da liễu, điều trị mụn trứng cá và chăm sóc da chuyên sâu."
        },
        {
            "id": "doctor_003",
            "name": "Bác sĩ Lê Thành Mạnh", 
            "title": "Dr. Mạnh",
            "specialty": "Bác sĩ Nhi khoa",
            "specialties": ["Nhi khoa", "Tiêm chủng trẻ em", "Dinh dưỡng trẻ em"],
            "experience": "10 năm",
            "education": "Thạc sĩ Y khoa - Bệnh viện Nhi Trung ương",
            "languages": ["Tiếng Việt", "English"],
            "available_days": ["Thứ 3", "Thứ 5", "Thứ 6", "Thứ 7"],
            "available_hours": "9:00 - 16:00",
            "consultation_fee": 300000,  # VND
            "description": "Bác sĩ nhi khoa giàu kinh nghiệm, chuyên về chăm sóc sức khỏe trẻ em và tư vấn dinh dưỡng."
        },
        {
            "id": "doctor_004",
            "name": "Bác sĩ Trần Minh Phước",
            "title": "Dr. Phước", 
            "specialty": "Bác sĩ Tai Mũi Họng",
            "specialties": ["Tai Mũi Họng", "Phẫu thuật TMH", "Nội soi"],
            "experience": "7 năm",
            "education": "Bác sĩ Y khoa - ĐH Y Huế",
            "languages": ["Tiếng Việt"],
            "available_days": ["Thứ 2", "Thứ 3", "Thứ 5", "Thứ 6"],
            "available_hours": "8:00 - 17:00",
            "consultation_fee": 280000,  # VND
            "description": "Chuyên khoa Tai Mũi Họng, có kỹ năng phẫu thuật và nội soi chuyên sâu."
        },
        {
            "id": "doctor_005",
            "name": "Bác sĩ Nguyễn Minh Quang",
            "title": "Dr. Quang",
            "specialty": "Bác sĩ Mắt",
            "specialties": ["Khoa mắt", "Phẫu thuật mắt", "Khúc xạ mắt"],
            "experience": "5 năm", 
            "education": "Bác sĩ Y khoa - ĐH Y Thái Bình",
            "languages": ["Tiếng Việt", "English"],
            "available_days": ["Thứ 2", "Thứ 4", "Thứ 6", "Thứ 7"],
            "available_hours": "9:30 - 17:00",
            "consultation_fee": 270000,  # VND
            "description": "Bác sĩ chuyên khoa mắt, điều trị các bệnh về mắt và phẫu thuật khúc xạ."
        }
    ]
}
