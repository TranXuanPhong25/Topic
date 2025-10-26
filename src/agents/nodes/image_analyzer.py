"""
ImageAnalyzer Node: Analyzes medical images using Gemini Vision.
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

logger = logging.getLogger(__name__)


class ImageAnalyzerNode:
    """
    ImageAnalyzer Node: Analyzes image in context of symptoms.
    """
    
    def __init__(self, vision_analyzer):
        """
        Initialize the ImageAnalyzer node.
        
        Args:
            vision_analyzer: Gemini Vision analyzer for medical images
        """
        self.vision_analyzer = vision_analyzer
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the image analyzer logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with image analysis results
        """
        logger.info("🔍 ImageAnalyzer: Analyzing medical image...")
        
        image = state.get("image")
        symptoms = state.get("symptoms", "")
        
        try:
            if not image:
                raise ValueError("No image provided")
            
            # Analyze image using GeminiVisionAnalyzer
            analysis_result = self.vision_analyzer.analyze_image(image, symptoms)
            
            state["image_analysis_result"] = analysis_result
            state["messages"].append("✅ ImageAnalyzer: Image analyzed successfully")
            
            logger.info(f"Image analysis confidence: {analysis_result.get('confidence', 0)}")
            
        except Exception as e:
            logger.error(f"ImageAnalyzer error: {str(e)}")
            state["image_analysis_result"] = {
                "visual_description": "",
                "visual_qa_results": {},
                "confidence": 0.0,
                "error": str(e)
            }
            state["messages"].append(f"❌ ImageAnalyzer: Error - {str(e)}")
        
        return state
