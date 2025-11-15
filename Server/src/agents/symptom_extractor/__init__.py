"""
Symptom Extractor Agent
Extracts and structures symptoms from patient conversations
"""
from .config import get_symptom_extractor_model
from .symptom_extractor import SymptomExtractorNode


def new_symptom_extractor_node():
    model = get_symptom_extractor_model()
    return SymptomExtractorNode(model)


__all__ = ["SymptomExtractorNode", "new_symptom_extractor_node"]
   