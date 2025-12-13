from src.agents.image_analyzer.config import get_image_analyzer_model
from .image_analyzer import ImageAnalyzerNode
from .lesion_classifier import get_lesion_classifier

def new_image_analyzer_node():
    model = get_image_analyzer_model()
    lesion = get_lesion_classifier()
    return ImageAnalyzerNode(model, lesion)

__all__ = ["ImageAnalyzerNode", "new_image_analyzer_node"]
