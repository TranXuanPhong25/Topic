from src.models.state import GraphState


class ImageAnalyzerNode:
    """Runs a local lesion classifier (if available) and forwards the prediction
    to Gemini for interpretation. Falls back to image-based analysis if the
    classifier is not present or fails.
    """

    def __init__(self, vision_analyzer, lesion_classifier=None):
        self.vision_analyzer = vision_analyzer
        self.lesion_classifier = lesion_classifier

    def __call__(self, state: "GraphState") -> "GraphState":
        print("=============== ImageAnalyzer ===============")

        image = state.get("image")
        symptoms = state.get("symptoms", "")

        try:
            if not image:
                raise ValueError("No image provided")

            analysis_result = {}

            if self.lesion_classifier is not None:
                try:
                    lesion_result = self.lesion_classifier.classify_base64(image)
                    analysis_result["lesion_classification"] = lesion_result

                    try:
                        gemini_interpretation = self.vision_analyzer.analyze_prediction(
                            lesion_result, symptoms
                        )
                        analysis_result["gemini_interpretation"] = gemini_interpretation
                    except Exception as gi_err:
                        analysis_result["gemini_interpretation"] = {
                            "error": f"Gemini interpretation failed: {str(gi_err)}"
                        }

                except Exception as lc_err:
                    analysis_result["lesion_classification"] = {"error": str(lc_err)}
                    print(f"Local classifier failed: {str(lc_err)} - falling back to image analysis")
                    analysis_result.update(self.vision_analyzer.analyze_image(image, symptoms))

            else:
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
