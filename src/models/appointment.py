"""Database models for Medical Clinic Chatbot"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Appointment(Base):
    """Appointment model for storing patient appointments"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(100), nullable=False, index=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    time = Column(String(5), nullable=False)   # HH:MM format
    reason = Column(Text, nullable=True)
    provider = Column(String(100), nullable=True)
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to todos
    todos = relationship("Todo", back_populates="appointment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient={self.patient_name}, date={self.date}, time={self.time})>"
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            "id": self.id,
            "patient_name": self.patient_name,
            "date": self.date,
            "time": self.time,
            "reason": self.reason,
            "provider": self.provider,
            "status": self.status,
            "phone": self.phone,
            "email": self.email,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


