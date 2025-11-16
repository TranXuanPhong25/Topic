"""Diagnosis Engine Agent - Medical diagnosis based on symptoms"""
from src.agents.diagnosis_engine.config import get_diagnosis_model
from .diagnosis_engine import DiagnosisEngineNode
def new_diagnosis_engine_node():
    model = get_diagnosis_model()
    return DiagnosisEngineNode(model)
__all__ = ["DiagnosisEngineNode", "new_diagnosis_engine_node"]
