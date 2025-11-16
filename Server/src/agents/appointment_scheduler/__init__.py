"""Appointment Scheduler Agent - Handle appointment booking"""
from .appointment_scheduler import AppointmentSchedulerNode
from .config import get_appointment_model


def new_appointment_scheduler_node():
    model = get_appointment_model()
    return AppointmentSchedulerNode(model)
__all__ = ["AppointmentSchedulerNode", "new_appointment_scheduler_node"]