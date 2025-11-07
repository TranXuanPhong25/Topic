"""
ImageAnalyzer Node: Analyzes medical images using Gemini Vision.
"""
from src.models.state import GraphState


class ImageAnalyzerNode:

    def __init__(self, vision_analyzer):
        self.vision_analyzer = vision_analyzer

    def __call__(self, state: "GraphState") -> "GraphState":
        print("=============== ImageAnalyzer ===============")

        image = state.get("image")
        symptoms = state.get("symptoms", "")

        try:
            if not image:
                raise ValueError("No image provided")

            # Analyze image using GeminiVisionAnalyzer
            analysis_result = self.vision_analyzer.analyze_image(image, symptoms)

            state["image_analysis_result"] = analysis_result
            state["current_step"] += 1

            print(f"Image analysis confidence: {analysis_result.get('confidence', 0)}")

        except Exception as e:
            print(f"ImageAnalyzer error: {str(e)}")
            state["image_analysis_result"] = {
                "visual_description": "",
                "visual_qa_results": {},
                "confidence": 0.0,
                "error": str(e)
            }

        return state
