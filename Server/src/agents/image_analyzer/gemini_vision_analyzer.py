"""
Gemini Vision Analyzer for medical image analysis using Gemini 2.0 Flash Lite.

This module provides vision analysis capabilities using Google's Gemini 2.0 Flash Lite model,
which supports multimodal input (text + images) for analyzing medical images.
"""

import base64
from typing import Dict, Any, Optional
from PIL import Image
import io
from src.configs.agent_config import HumanMessage

class GeminiVisionAnalyzer:
    """
    Vision analyzer using Gemini 2.0 Flash Lite for medical image analysis.
    
    This class provides:
    - Image description and analysis
    - Visual Q&A based on symptoms
    - Medical image interpretation
    - Confidence scoring
    """
    
    def __init__(self, model):
       self.model = model
    
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
            
            print(f"Vision analysis complete. Confidence: {confidence:.2f}")
            return result
            
        except Exception as e:
            print(f"Vision analysis error: {str(e)}")
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
            
            print(f"Decoded image: {image.size}, mode: {image.mode}")
            return image
            
        except Exception as e:
            print(f"Error decoding image: {str(e)}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    def _pil_image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string for LangChain vision input.
        
        Args:
            image: PIL Image object
        
        Returns:
            Base64 encoded image string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
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
            image_base64 = self._pil_image_to_base64(image)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            response = self.model.invoke([message])
            description = response.content.strip()
            
            print(f"Generated visual description: {description[:100]}...")
            return description
            
        except Exception as e:
            print(f"Error generating visual description: {str(e)}")
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
                image_base64 = self._pil_image_to_base64(image)
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                )
                response = self.model.invoke([message])
                answer = response.content.strip()
                qa_results[question] = answer
                print(f"Q: {question[:50]}... A: {answer[:50]}...")
                
            except Exception as e:
                print(f"Error in visual QA: {str(e)}")
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
                                    
            image_base64 = self._pil_image_to_base64(image)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            response = self.model.invoke([message])
            analysis = response.content.strip()
            
            return {
                "analysis": analysis,
                "type": "skin_condition",
                "confidence": 0.85 if len(analysis) > 100 else 0.6,
                "error": None
            }
            
        except Exception as e:
            print(f"Skin analysis error: {str(e)}")
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
            
            image_base64 = self._pil_image_to_base64(image)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            response = self.model.invoke([message])
            analysis = response.content.strip()
            
            return {
                "analysis": analysis,
                "type": "wound",
                "confidence": 0.85 if len(analysis) > 100 else 0.6,
                "error": None
            }
            
        except Exception as e:
            print(f"Wound analysis error: {str(e)}")
            return {
                "analysis": "",
                "type": "wound",
                "confidence": 0.0,
                "error": str(e)
            }

    def classify_image_type(
        self, 
        image_data: str, 
        user_input: str = ""
    ) -> Dict[str, Any]:
        """
        Classify the type of image and determine if it's for diagnostic purposes.
        
        Args:
            image_data: Base64 encoded image string
            user_input: User's text input for context
        
        Returns:
            Dictionary containing:
            - image_type: "medical", "document", "general", "unclear"
            - is_diagnostic: Whether the image is for medical diagnosis
            - intent: Detected user intent for the image
            - confidence: Classification confidence
        """
        try:
            image = self._decode_base64_image(image_data)
            
            context_hint = f"\n**Ngữ cảnh từ người dùng:** {user_input}" if user_input else ""
            
            prompt = f"""Bạn là chuyên gia phân loại hình ảnh y tế. Hãy xác định loại hình ảnh.
{context_hint}

**QUAN TRỌNG - Phân loại hình ảnh thành MỘT trong các loại sau:**

1. **document** - Tài liệu y tế bao gồm:
   - Đơn thuốc (có tên thuốc, liều lượng, hướng dẫn sử dụng)
   - Kết quả xét nghiệm (có số liệu, chỉ số, giá trị)
   - Giấy khám bệnh, phiếu khám
   - Hóa đơn y tế, biên lai
   - Toa thuốc viết tay hoặc in
   - Bất kỳ giấy tờ/văn bản nào liên quan y tế
   - **DẤU HIỆU NHẬN BIẾT**: có chữ viết, bảng biểu, logo bệnh viện/phòng khám, format giấy tờ

2. **medical** - Ảnh y tế để chẩn đoán:
   - Ảnh da, vết thương, phát ban, mụn
   - Vùng cơ thể bị đau, sưng, viêm
   - Triệu chứng nhìn thấy được trên cơ thể
   - **DẤU HIỆU NHẬN BIẾT**: ảnh chụp trực tiếp cơ thể người

3. **general** - Ảnh chung không liên quan y tế:
   - Ảnh chân dung, selfie bình thường
   - Phong cảnh, đồ vật, thức ăn
   - Ảnh không liên quan đến sức khỏe

4. **unclear** - CHỈ dùng khi THỰC SỰ không thể xác định

**⚠️ LƯU Ý QUAN TRỌNG:**
- Nếu thấy CHỮ VIẾT hoặc FORMAT GIẤY TỜ → ưu tiên phân loại là **document**
- Nếu người dùng hỏi về "đơn thuốc", "toa thuốc", "kết quả xét nghiệm" → phân loại là **document**
- TRÁNH phân loại là "unclear" trừ khi thật sự không nhìn thấy gì

**Trả lời theo định dạng sau (CHÍNH XÁC):**
LOẠI: [medical/document/general/unclear]
CHẨN_ĐOÁN: [có/không]
Ý_ĐỊNH: [mô tả ngắn gọn mục đích của người dùng khi gửi ảnh]
ĐỘ_TIN_CẬY: [cao/trung bình/thấp]

**Phân loại:**"""
            
            print(f"🔍 Classifying image with user context: {user_input[:50] if user_input else 'None'}...")
            
            image_base64 = self._pil_image_to_base64(image)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            response = self.model.invoke([message])
            result_text = response.content.strip()
            
            print(f"🔍 Classification raw response: {result_text[:200]}...")
            
            # Parse the response
            image_type = "unclear"
            is_diagnostic = False
            intent = ""
            confidence = 0.5
            
            lines = result_text.split("\n")
            for line in lines:
                line_lower = line.lower().strip()
                if line_lower.startswith("loại:"):
                    type_value = line.split(":", 1)[1].strip().lower()
                    # Handle variations in response
                    if "document" in type_value or "tài liệu" in type_value:
                        image_type = "document"
                    elif "medical" in type_value or "y tế" in type_value:
                        image_type = "medical"
                    elif "general" in type_value or "chung" in type_value:
                        image_type = "general"
                    elif type_value in ["medical", "document", "general", "unclear"]:
                        image_type = type_value
                elif line_lower.startswith("chẩn_đoán:"):
                    diag_value = line.split(":", 1)[1].strip().lower()
                    is_diagnostic = diag_value in ["có", "yes", "true", "1"]
                elif line_lower.startswith("ý_định:"):
                    intent = line.split(":", 1)[1].strip()
                elif line_lower.startswith("độ_tin_cậy:"):
                    conf_value = line.split(":", 1)[1].strip().lower()
                    if conf_value == "cao" or "cao" in conf_value:
                        confidence = 0.9
                    elif conf_value == "trung bình" or "trung" in conf_value:
                        confidence = 0.7
                    else:
                        confidence = 0.5
            
            # Fallback: check for document keywords in response if still unclear
            if image_type == "unclear":
                result_lower = result_text.lower()
                if any(kw in result_lower for kw in ["đơn thuốc", "toa thuốc", "prescription", "kết quả xét nghiệm", "test result", "giấy khám", "phiếu khám"]):
                    print("🔍 Fallback: Detected document keywords in response, changing type to document")
                    image_type = "document"
            
            # Force correct diagnostic status based on image type
            # Only medical images can be diagnostic
            if image_type == "medical":
                is_diagnostic = True
            elif image_type in ["document", "general"]:
                # Documents and general images are NOT for medical diagnosis
                is_diagnostic = False
            # For unclear, keep whatever LLM returned
            
            print(f"🔍 Image classification: type={image_type}, diagnostic={is_diagnostic}, confidence={confidence}")
            
            return {
                "image_type": image_type,
                "is_diagnostic": is_diagnostic,
                "intent": intent,
                "confidence": confidence,
                "raw_response": result_text
            }
            
        except Exception as e:
            print(f"Image classification error: {str(e)}")
            # Default to medical/diagnostic on error to be safe
            return {
                "image_type": "medical",
                "is_diagnostic": True,
                "intent": "Không thể xác định",
                "confidence": 0.3,
                "error": str(e)
            }

    def analyze_document(
        self, 
        image_data: str, 
        user_input: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a document image (prescription, test result, etc.)
        
        Args:
            image_data: Base64 encoded image string
            user_input: User's text input for context
        
        Returns:
            Dictionary containing document analysis results
        """
        try:
            image = self._decode_base64_image(image_data)
            
            context_hint = f"\n**Yêu cầu từ người dùng:** {user_input}" if user_input else ""
            
            prompt = f"""Bạn là chuyên gia đọc và trích xuất thông tin từ tài liệu y tế. Hãy phân tích CHI TIẾT hình ảnh tài liệu này.
{context_hint}

**QUAN TRỌNG - Nhiệm vụ của bạn:**
1. **Xác định loại tài liệu**: Đơn thuốc, kết quả xét nghiệm, giấy khám bệnh, hay loại khác?

2. **Nếu là ĐƠN THUỐC - Trích xuất TỪNG THUỐC với format sau:**
   - Tên thuốc: [tên đầy đủ]
   - Liều lượng: [số lượng, mg/ml nếu có]
   - Cách dùng: [ngày mấy lần, uống/bôi/tiêm...]
   - Thời gian: [trước/sau ăn, sáng/trưa/tối]
   - Số lượng: [bao nhiêu viên/lọ/...]

3. **Nếu là KẾT QUẢ XÉT NGHIỆM - Trích xuất từng chỉ số:**
   - Tên xét nghiệm: [tên]
   - Kết quả: [giá trị]
   - Đơn vị: [đơn vị đo]
   - Phạm vi bình thường: [nếu có]

4. **Thông tin bổ sung:**
   - Tên bệnh nhân (nếu có)
   - Tên bác sĩ/cơ sở y tế (nếu có)
   - Ngày kê đơn/xét nghiệm (nếu có)
   - Chẩn đoán/ghi chú (nếu có)

**Lưu ý:**
- Trích xuất TẤT CẢ thông tin có thể đọc được
- Ghi rõ "[không đọc được]" cho phần mờ/không rõ
- KHÔNG đưa ra lời khuyên y tế hay chẩn đoán
- Viết CHI TIẾT và CỤ THỂ

**Phân tích tài liệu:**"""
            
            image_base64 = self._pil_image_to_base64(image)
            
            print(f"📄 Sending document to LLM for analysis...")
            print(f"📄 Image base64 length: {len(image_base64)} chars")
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            
            try:
                response = self.model.invoke([message])
                print(f"📄 Raw response type: {type(response)}")
                print(f"📄 Raw response: {response}")
                
                if hasattr(response, 'content'):
                    content = response.content.strip() if response.content else ""
                else:
                    content = str(response).strip()
                    
            except Exception as invoke_error:
                print(f"❌ LLM invoke error: {invoke_error}")
                import traceback
                traceback.print_exc()
                content = ""
            
            print(f"📄 Document analysis response length: {len(content)} chars")
            if content:
                print(f"📄 Document analysis preview: {content[:300]}...")
            else:
                print("⚠️ Document analysis returned empty content!")
            
            # Try to detect document type from response
            doc_type = "unknown"
            content_lower = content.lower()
            if "đơn thuốc" in content_lower or "prescription" in content_lower:
                doc_type = "prescription"
            elif "xét nghiệm" in content_lower or "kết quả" in content_lower or "test" in content_lower:
                doc_type = "test_result"
            elif "giấy khám" in content_lower or "phiếu khám" in content_lower:
                doc_type = "medical_record"
            elif "hóa đơn" in content_lower:
                doc_type = "invoice"
            
            return {
                "description": "Phân tích tài liệu y tế",
                "content": content,
                "type": doc_type,
                "confidence": 0.8 if len(content) > 100 else 0.5,
                "error": None
            }
            
        except Exception as e:
            print(f"Document analysis error: {str(e)}")
            return {
                "description": "",
                "content": "",
                "type": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }