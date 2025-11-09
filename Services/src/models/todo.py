"""Database models for Medical Clinic Chatbot"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Todo(Base):
    """Todo/Task model for clinic staff"""
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # appointment, followup, callback, prescription
    priority = Column(String(20), default="medium")  # urgent, high, medium, low
    assignee = Column(String(100), nullable=True)  # doctor, nurse, admin, etc.
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to appointment (optional)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    appointment = relationship("Appointment", back_populates="todos")
    
    # Conversation session reference
    session_id = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Todo(id={self.id}, title={self.title}, priority={self.priority}, status={self.status})>"
    
    def to_dict(self):
        """Convert todo to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "assignee": self.assignee,
            "status": self.status,
            "due_date": self.due_date.isoformat() ,
            "completed_at": self.completed_at.isoformat() ,
            "created_at": self.created_at.isoformat() ,
            "updated_at": self.updated_at.isoformat() ,
            "appointment_id": self.appointment_id,
            "session_id": self.session_id,
        }
