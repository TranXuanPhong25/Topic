from src.models.state import GraphState
from typing import Dict, Any, Tuple


class ImageAnalyzerNode:
    """Runs a local lesion classifier (if available) and forwards the prediction
    to Gemini for interpretation. Falls back to image-based analysis if the
    classifier is not present or fails.
    
    This node also classifies the image type to determine if it's for diagnostic
    purposes or not (e.g., document, general photo, etc.)
    """

    # Image type constants
    IMAGE_TYPE_MEDICAL = "medical"  # Medical/diagnostic image (skin, wound, body part)
    IMAGE_TYPE_DOCUMENT = "document"  # Document, prescription, test result
    IMAGE_TYPE_GENERAL = "general"  # General photo, not for diagnosis
    IMAGE_TYPE_UNCLEAR = "unclear"  # Cannot determine

    def __init__(self, vision_analyzer, lesion_classifier=None):
        self.vision_analyzer = vision_analyzer
        self.lesion_classifier = lesion_classifier
    
    def _get_current_goal(self, state: "GraphState") -> str:
        """
        Extract the goal for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Goal string or empty string if not found
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return ""
        
        current_plan_step = plan[current_step_index]
        goal = current_plan_step.get("goal", "")
        
        if goal:
            print(f"🎯 Current Goal: {goal}")
        
        return goal
    
    def _get_current_context(self, state: "GraphState") -> dict:
        """
        Extract context and user_context for the current step from the plan
        
        Args:
            state: Current graph state
            
        Returns:
            Dict with 'context' and 'user_context' keys (empty strings if not found)
        """
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return {"context": "", "user_context": ""}
        
        current_plan_step = plan[current_step_index]
        context = current_plan_step.get("context", "")
        user_context = current_plan_step.get("user_context", "")
        
        if context:
            print(f"📝 Context: {context[:100]}...")
        if user_context:
            print(f"👤 User Context: {user_context[:100]}...")
        
        return {"context": context, "user_context": user_context}

    def _classify_image_type(self, image: str, user_input: str = "") -> Tuple[str, bool, str]:
        """
        Classify the image to determine its type and whether it's for diagnosis.
        
        Args:
            image: Base64 encoded image
            user_input: User's text input for context
            
        Returns:
            Tuple of (image_type, is_diagnostic, intent)
        """
        try:
            classification_result = self.vision_analyzer.classify_image_type(image, user_input)
            
            image_type = classification_result.get("image_type", self.IMAGE_TYPE_UNCLEAR)
            is_diagnostic = classification_result.get("is_diagnostic", False)
            intent = classification_result.get("intent", "")
            
            print(f"📷 Image classification: type={image_type}, diagnostic={is_diagnostic}")
            if intent:
                print(f"   Intent: {intent}")
            
            return image_type, is_diagnostic, intent
            
        except Exception as e:
            print(f"⚠️ Image classification failed: {e}, defaulting to medical")
            # Default to medical image if classification fails
            return self.IMAGE_TYPE_MEDICAL, True, ""

    def __call__(self, state: "GraphState") -> "GraphState":
        print("=============== ImageAnalyzer ===============")

        image = state.get("image")
        symptoms = state.get("symptoms", "")
        user_input = state.get("input", "")

        try:
            if not image:
                raise ValueError("No image provided")

            # First, classify the image type
            image_type, is_diagnostic, intent = self._classify_image_type(image, user_input)
            
            # Store classification results in state
            state["image_type"] = image_type
            state["is_diagnostic_image"] = is_diagnostic
            state["image_analysis_intent"] = intent

            analysis_result = {}
            
            # Handle based on image type
            if not is_diagnostic:
                # Image is not for diagnosis - provide appropriate response
                print(f"📷 Non-diagnostic image detected: {image_type}")
                
                if image_type == self.IMAGE_TYPE_DOCUMENT:
                    # Document/prescription - extract text info
                    analysis_result = self._analyze_document_image(image, user_input)
                    # Debug: print document content
                    doc_content = analysis_result.get("document_content", "")
                    print(f"📄 Document content extracted: {len(doc_content)} chars")
                    if doc_content:
                        print(f"📄 Preview: {doc_content[:200]}...")
                elif image_type == self.IMAGE_TYPE_GENERAL:
                    # General photo - acknowledge but don't analyze medically
                    analysis_result = {
                        "visual_description": "Hình ảnh không phải là ảnh y tế để chẩn đoán.",
                        "image_type": image_type,
                        "is_diagnostic": False,
                        "message": "Hình ảnh này không phải là ảnh y tế. Nếu bạn muốn được tư vấn về vấn đề sức khỏe, vui lòng gửi ảnh vùng da/bộ phận cơ thể cần kiểm tra.",
                        "confidence": 0.0
                    }
                else:
                    # Unclear - ask for clarification
                    analysis_result = {
                        "visual_description": "Không thể xác định mục đích của hình ảnh.",
                        "image_type": image_type,
                        "is_diagnostic": False,
                        "message": "Tôi không chắc chắn về mục đích của hình ảnh này. Bạn có thể cho tôi biết bạn muốn tôi giúp gì với hình ảnh này không?",
                        "confidence": 0.0,
                        "needs_clarification": True
                    }
            else:
                # Diagnostic image - proceed with medical analysis
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
                
                # Add diagnostic flag
                analysis_result["is_diagnostic"] = True
                analysis_result["image_type"] = image_type

            state["image_analysis_result"] = analysis_result
            state["current_step"] += 1

            print(f"Image analysis complete. Type: {image_type}, Diagnostic: {is_diagnostic}")
            print(f"Confidence: {analysis_result.get('confidence', 0)}")

        except Exception as e:
            print(f"ImageAnalyzer error: {str(e)}")
            state["image_analysis_result"] = {
                "visual_description": "",
                "visual_qa_results": {},
                "confidence": 0.0,
                "error": str(e),
                "is_diagnostic": False,
                "image_type": self.IMAGE_TYPE_UNCLEAR
            }
            state["image_type"] = self.IMAGE_TYPE_UNCLEAR
            state["is_diagnostic_image"] = False

        return state

    def _analyze_document_image(self, image: str, user_input: str) -> Dict[str, Any]:
        """
        Analyze a document image (prescription, test result, etc.)
        
        Args:
            image: Base64 encoded image
            user_input: User's text input for context
            
        Returns:
            Analysis result dict
        """
        try:
            print(f"📄 Analyzing document image with user input: {user_input[:100] if user_input else 'None'}...")
            
            # Use vision analyzer to extract document information
            doc_result = self.vision_analyzer.analyze_document(image, user_input)
            
            document_content = doc_result.get("content", "")
            document_type = doc_result.get("type", "unknown")
            
            print(f"📄 Document type detected: {document_type}")
            print(f"📄 Document content length: {len(document_content)} chars")
            if document_content:
                print(f"📄 Content preview: {document_content[:200]}...")
            else:
                print("⚠️ No document content extracted!")
            
            return {
                "visual_description": doc_result.get("description", "Phân tích tài liệu y tế"),
                "document_content": document_content,
                "document_type": document_type,
                "image_type": self.IMAGE_TYPE_DOCUMENT,
                "is_diagnostic": False,
                "confidence": doc_result.get("confidence", 0.5)
            }
        except Exception as e:
            print(f"❌ Document analysis error: {str(e)}")
            return {
                "visual_description": "Đây là hình ảnh tài liệu/đơn thuốc.",
                "image_type": self.IMAGE_TYPE_DOCUMENT,
                "is_diagnostic": False,
                "message": "Tôi nhận ra đây là hình ảnh tài liệu. Bạn có thể cho tôi biết bạn cần hỗ trợ gì với tài liệu này?",
                "confidence": 0.3,
                "error": str(e)
            }
