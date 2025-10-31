"""Image Analyzer Agent - Medical image analysis"""
from src.agents.image_analyzer.config import get_image_analyzer_model
from .image_analyzer import ImageAnalyzerNode

def new_image_analyzer_node():
    model = get_image_analyzer_model()
    return ImageAnalyzerNode(model)

__all__ = ["ImageAnalyzerNode", "new_image_analyzer_node"]
