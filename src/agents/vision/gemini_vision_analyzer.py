"""
Gemini Vision Analyzer for medical image analysis using Gemini 2.0 Flash Lite.

This module provides vision analysis capabilities using Google's Gemini 2.0 Flash Lite model,
which supports multimodal input (text + images) for analyzing medical images.
"""

import base64
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
import io
from configs.agent_config import VISION_CONFIG

logger = logging.getLogger(__name__)


class GeminiVisionAnalyzer:
    """
    Vision analyzer using Gemini 2.0 Flash Lite for medical image analysis.
    
    This class provides:
    - Image description and analysis
    - Visual Q&A based on symptoms
    - Medical image interpretation
    - Confidence scoring
    """
    
    def __init__(self, google_api_key: str):
        """
        Initialize the Gemini Vision Analyzer.
        
        Args:
            google_api_key: Google API key for Gemini
        """
        self.google_api_key = google_api_key
        
        # Configure Gemini
        genai.configure(api_key=google_api_key)
        
        # Initialize Gemini model for vision using centralized config
        self.model = genai.GenerativeModel(
            model_name=VISION_CONFIG["model_name"],
            generation_config=VISION_CONFIG["generation_config"],
            safety_settings=VISION_CONFIG["safety_settings"]
        )
        
        logger.info(f"GeminiVisionAnalyzer initialized with {VISION_CONFIG['model_name']}")
    
    def analyze_image(
        self, 
        image_data: str, 
        symptoms_text: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a medical image using Gemini Vision.
        
        Args:
            image_data: Base64 encoded image string
            symptoms_text: Optional text description of symptoms
        
        Returns:
            Dictionary containing:
            - visual_description: Detailed description of the image
            - visual_qa_results: Answers to symptom-specific questions
            - confidence: Confidence score (0-1)
            - error: Error message if any
        """
        logger.info("Starting Gemini vision analysis...")
        
        try:
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            
            # Generate visual description
            visual_description = self._generate_visual_description(image)
            
            # Perform visual Q&A if symptoms provided
            visual_qa_results = {}
            if symptoms_text and symptoms_text.strip():
                visual_qa_results = self._perform_visual_qa(image, symptoms_text)
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(visual_description, visual_qa_results)
            
            result = {
                "visual_description": visual_description,
                "visual_qa_results": visual_qa_results,
                "confidence": confidence,
                "error": None
            }
            
            logger.info(f"Vision analysis complete. Confidence: {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Vision analysis error: {str(e)}")
            return {
                "visual_description": "",
                "visual_qa_results": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _decode_base64_image(self, image_data: str) -> Image.Image:
        """
        Decode base64 image string to PIL Image.
        
        Args:
            image_data: Base64 encoded image string
        
        Returns:
            PIL Image object
        """
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',', 1)[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"Decoded image: {image.size}, mode: {image.mode}")
            return image
            
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    def _generate_visual_description(self, image: Image.Image) -> str:
        """
        Generate a detailed description of the medical image using Gemini Vision.
        
        Args:
            image: PIL Image object
        
        Returns:
            Detailed visual description
        """
        prompt = """Bạn là chuyên gia phân tích hình ảnh y tế. Hãy mô tả chi tiết những gì bạn thấy trong hình ảnh này.

                    **Nhiệm vụ:**
                    Cung cấp mô tả khách quan, chi tiết về:
                    1. Loại hình ảnh (da, vết thương, phần cơ thể, v.v.)
                    2. Màu sắc và kết cấu quan sát được
                    3. Kích thước và vị trí (nếu có thể xác định)
                    4. Bất kỳ đặc điểm bất thường nào
                    5. Các chi tiết có liên quan đến y tế

                    **Lưu ý:**
                    - Chỉ mô tả những gì bạn thấy, KHÔNG chẩn đoán
                    - Sử dụng thuật ngữ y tế khi thích hợp
                    - Viết bằng tiếng Việt, rõ ràng và chính xác
                    - Khoảng 4-6 câu

                    **Mô tả hình ảnh:**"""
        
        try:
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            description = response.text.strip()
            
            logger.info(f"Generated visual description: {description[:100]}...")
            return description
            
        except Exception as e:
            logger.error(f"Error generating visual description: {str(e)}")
            return f"Không thể phân tích hình ảnh: {str(e)}"
    
    def _perform_visual_qa(
        self, 
        image: Image.Image, 
        symptoms_text: str
    ) -> Dict[str, str]:
        """
        Perform visual question answering based on symptoms.
        
        Args:
            image: PIL Image object
            symptoms_text: Patient's symptom description
        
        Returns:
            Dictionary of questions and answers
        """
        # Generate relevant questions based on symptoms
        questions = self._generate_questions(symptoms_text)
        
        qa_results = {}
        
        for question in questions:
            prompt = f"""Bạn là chuyên gia phân tích hình ảnh y tế. 

                        **Triệu chứng của bệnh nhân:** {symptoms_text}

                        **Câu hỏi:** {question}

                        **Nhiệm vụ:**
                        Trả lời câu hỏi dựa trên những gì bạn thấy trong hình ảnh.
                        - Trả lời ngắn gọn, trực tiếp (1-2 câu)
                        - Chỉ dựa trên hình ảnh, không đưa ra chẩn đoán
                        - Viết bằng tiếng Việt

                        **Trả lời:**"""
                                    
            try:
                response = self.model.generate_content([prompt, image])
                answer = response.text.strip()
                qa_results[question] = answer
                logger.info(f"Q: {question[:50]}... A: {answer[:50]}...")
                
            except Exception as e:
                logger.error(f"Error in visual QA: {str(e)}")
                qa_results[question] = f"Không thể trả lời: {str(e)}"
        
        return qa_results
    
    def _generate_questions(self, symptoms_text: str) -> list:
        """
        Generate relevant questions based on symptoms.
        
        Args:
            symptoms_text: Patient's symptom description
        
        Returns:
            List of relevant questions to ask about the image
        """
        # Default medical image questions
        default_questions = [
            "Có thấy dấu hiệu sưng tấy không?",
            "Màu sắc có bất thường không?",
            "Có thấy dấu hiệu nhiễm trùng không?",
        ]
        
        # Keyword-based question generation
        questions = default_questions.copy()
        
        symptoms_lower = symptoms_text.lower()
        
        if any(word in symptoms_lower for word in ['đỏ', 'đỏ', 'sưng', 'phồng']):
            questions.append("Mức độ đỏ và sưng như thế nào?")
        
        if any(word in symptoms_lower for word in ['đau', 'nhức', 'đớn']):
            questions.append("Có dấu hiệu gì cho thấy nguyên nhân đau không?")
        
        if any(word in symptoms_lower for word in ['vết', 'thương', 'rách', 'xước']):
            questions.append("Vết thương trông có sạch sẽ không?")
        
        if any(word in symptoms_lower for word in ['phát ban', 'mẩn', 'nổi']):
            questions.append("Phát ban trông như thế nào (màu sắc, hình dạng)?")
        
        # Limit to 5 questions max
        return questions[:5]
    
    def _calculate_confidence(
        self, 
        description: str, 
        qa_results: Dict[str, str]
    ) -> float:
        """
        Calculate confidence score based on analysis quality.
        
        Args:
            description: Visual description text
            qa_results: Q&A results dictionary
        
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.0
        
        # Base confidence from description quality
        if description and len(description) > 50:
            confidence += 0.5
        elif description and len(description) > 20:
            confidence += 0.3
        
        # Add confidence from Q&A results
        if qa_results:
            successful_answers = sum(
                1 for answer in qa_results.values() 
                if answer and "Không thể" not in answer
            )
            qa_confidence = (successful_answers / len(qa_results)) * 0.5
            confidence += qa_confidence
        
        # Check for error indicators
        if "không thể" in description.lower() or "lỗi" in description.lower():
            confidence *= 0.5
        
        return min(confidence, 1.0)
    
    def analyze_skin_condition(
        self, 
        image_data: str, 
        specific_concern: str = ""
    ) -> Dict[str, Any]:
        """
        Specialized analysis for skin conditions.
        
        Args:
            image_data: Base64 encoded image
            specific_concern: Specific skin concern (e.g., "rash", "lesion")
        
        Returns:
            Detailed skin analysis
        """
        try:
            image = self._decode_base64_image(image_data)
            
            concern_text = f" về {specific_concern}" if specific_concern else ""
            
            prompt = f"""Bạn là chuyên gia da liễu phân tích hình ảnh. Hãy phân tích tình trạng da trong hình ảnh{concern_text}.

                        **Nhiệm vụ:** Cung cấp phân tích chi tiết về:
                        1. **Loại tổn thương:** Mô tả loại tổn thương da (mụn, phát ban, nốt ruồi, v.v.)
                        2. **Đặc điểm:** Màu sắc, kích thước, hình dạng, ranh giới
                        3. **Phân bố:** Khu trú hoặc lan rộng, đối xứng hay không
                        4. **Các dấu hiệu:** Sưng tấy, vảy, tiết dịch, v.v.
                        5. **Mức độ nghiêm trọng:** Nhẹ/Trung bình/Nặng

                        **Lưu ý:**
                        - Mô tả khách quan, không chẩn đoán chính xác
                        - Sử dụng thuật ngữ da liễu
                        - Viết bằng tiếng Việt
                        - Khoảng 5-7 câu

                        **Phân tích:**"""
                                    
            response = self.model.generate_content([prompt, image])
            analysis = response.text.strip()
            
            return {
                "analysis": analysis,
                "type": "skin_condition",
                "confidence": 0.85 if len(analysis) > 100 else 0.6,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Skin analysis error: {str(e)}")
            return {
                "analysis": "",
                "type": "skin_condition",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def analyze_wound(
        self, 
        image_data: str
    ) -> Dict[str, Any]:
        """
        Specialized analysis for wound assessment.
        
        Args:
            image_data: Base64 encoded image
        
        Returns:
            Detailed wound analysis
        """
        try:
            image = self._decode_base64_image(image_data)
            
            prompt = """Bạn là chuyên gia chăm sóc vết thương phân tích hình ảnh. Hãy đánh giá vết thương trong hình ảnh.

                        **Nhiệm vụ:** Phân tích:
                        1. **Loại vết thương:** Cắt, xước, bỏng, v.v.
                        2. **Kích thước và độ sâu:** Ước tính nếu có thể
                        3. **Tình trạng:** Sạch/nhiễm trùng, khô/ướt
                        4. **Dấu hiệu nhiễm trùng:** Mủ, đỏ, sưng, nóng
                        5. **Giai đoạn lành:** Mới/đang lành/đã lành
                        6. **Cần chăm sóc y tế:** Có/Không và tại sao

                        **Lưu ý:**
                        - Đánh giá khách quan
                        - Tập trung vào các dấu hiệu quan trọng
                        - Viết bằng tiếng Việt
                        - Khoảng 6-8 câu

                        **Đánh giá vết thương:**"""
            
            response = self.model.generate_content([prompt, image])
            analysis = response.text.strip()
            
            return {
                "analysis": analysis,
                "type": "wound",
                "confidence": 0.85 if len(analysis) > 100 else 0.6,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Wound analysis error: {str(e)}")
            return {
                "analysis": "",
                "type": "wound",
                "confidence": 0.0,
                "error": str(e)
            }
