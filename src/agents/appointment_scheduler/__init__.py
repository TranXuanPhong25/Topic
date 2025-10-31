"""Appointment Scheduler Agent - Handle appointment booking"""
from src.agents.appointment_scheduler.config import get_appointment_model
from .appointment_scheduler import AppointmentSchedulerNode
def new_appointment_scheduler_node(appointment_handler):
    model = get_appointment_model()
    return AppointmentSchedulerNode(model, appointment_handler)
__all__ = ["AppointmentSchedulerNode", "new_appointment_scheduler_node"]
