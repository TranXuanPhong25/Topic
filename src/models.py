"""Database models for Medical Clinic Chatbot"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "appointment_id": self.appointment_id,
            "session_id": self.session_id,
        }


class Conversation(Base):
    """Conversation history model for tracking chat sessions"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Optional metadata
    patient_name = Column(String(100), nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session={self.session_id}, role={self.role})>"
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "patient_name": self.patient_name,
            "extra_data": self.extra_data,
        }


class ClinicSettings(Base):
    """Clinic configuration and settings"""
    __tablename__ = "clinic_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ClinicSettings(key={self.key}, value={self.value})>"
    
    def to_dict(self):
        """Convert setting to dictionary"""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
