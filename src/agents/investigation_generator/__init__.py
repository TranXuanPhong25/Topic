"""Investigation Generator Agent - Suggest medical tests"""
from .config import get_investigation_model
from .investigation_generator import InvestigationGeneratorNode
def new_investigation_generator_node():
    model = get_investigation_model()
    return InvestigationGeneratorNode(model)
__all__ = ["InvestigationGeneratorNode", "new_investigation_generator_node"]
