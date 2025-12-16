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
        prompt = """You are a medical image analysis expert. Please provide a detailed description of what you see in this image.

                    **Task:**
                    Provide an objective, detailed description of:
                    1. Type of image (skin, wound, body part, etc.)
                    2. Observable colors and textures
                    3. Size and location (if identifiable)
                    4. Any abnormal features
                    5. Medically relevant details

                    **Important:**
                    - Only describe what you see, do NOT diagnose
                    - Use medical terminology when appropriate
                    - Write clearly and accurately
                    - Provide 4-6 sentences

                    **Image Description:**"""
        
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
            return f"Unable to analyze image: {str(e)}"
    
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
            prompt = f"""You are a medical image analysis expert. 

                        **Patient Symptoms:** {symptoms_text}

                        **Question:** {question}

                        **Task:**
                        Answer the question based on what you see in the image.
                        - Answer briefly and directly (1-2 sentences)
                        - Based only on the image, no diagnosis
                        - Write clearly and accurately

                        **Answer:**"""
                                    
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
                qa_results[question] = f"Unable to answer: {str(e)}"
        
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
            
            concern_text = f" regarding {specific_concern}" if specific_concern else ""
            
            prompt = f"""You are a dermatology image analysis expert. Please analyze the skin condition in this image{concern_text}.

                        **Task:** Provide detailed analysis of:
                        1. **Lesion Type:** Describe the type of skin lesion (acne, rash, mole, etc.)
                        2. **Characteristics:** Color, size, shape, borders
                        3. **Distribution:** Localized or widespread, symmetric or not
                        4. **Signs:** Swelling, scaling, discharge, etc.
                        5. **Severity:** Mild/Moderate/Severe

                        **Important:**
                        - Objective description, no definitive diagnosis
                        - Use dermatological terminology
                        - Write clearly and accurately
                        - Provide 5-7 sentences

                        **Analysis:**"""
                                    
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
            
            prompt = """You are a wound care analysis expert. Please assess the wound in this image.

                        **Task:** Analyze:
                        1. **Wound Type:** Cut, scratch, burn, etc.
                        2. **Size and Depth:** Estimate if possible
                        3. **Condition:** Clean/contaminated, dry/moist
                        4. **Infection Signs:** Pus, redness, swelling, warmth
                        5. **Healing Stage:** New/healing/healed
                        6. **Medical Care Needed:** Yes/No and why

                        **Important:**
                        - Objective assessment
                        - Focus on significant findings
                        - Write clearly and accurately
                        - Provide 6-8 sentences

                        **Wound Assessment:**"""
            
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
            
            prompt = f"""You are a medical image classification expert. Please identify the image type.
{context_hint}

**IMPORTANT - Classify the image into ONE of the following types:**

1. **document** - Medical documents including:
   - Prescriptions (with medication names, dosages, instructions)
   - Test results (with data, values, numbers)
   - Medical exam forms, records
   - Medical invoices, receipts
   - Handwritten or printed prescriptions
   - Any medical-related papers or documents
   - **IDENTIFYING SIGNS**: contains text, tables, hospital/clinic logos, document format

2. **medical** - Medical images for diagnosis:
   - Skin photos, wounds, rashes, acne
   - Affected body areas: swelling, inflammation, pain
   - Visible symptoms on the body
   - **IDENTIFYING SIGNS**: direct photos of human body/affected areas

3. **general** - Non-medical images:
   - Portrait photos, normal selfies
   - Landscapes, objects, food
   - Health-unrelated images

4. **unclear** - ONLY use when TRULY unable to determine

**IMPORTANT NOTES:**
- If you see TEXT or DOCUMENT FORMAT → prioritize classifying as **document**
- If user asks about "prescription", "medication", "test results" → classify as **document**
- AVOID using "unclear" unless truly unable to identify anything

**Answer in the following format (EXACT):**
TYPE: [medical/document/general/unclear]
DIAGNOSTIC: [yes/no]
PURPOSE: [brief description of user's intent in sending this image]
CONFIDENCE: [high/medium/low]

**Classification:**"""
            
            print(f"Classifying image with user context: {user_input[:50] if user_input else 'None'}...")
            
            image_base64 = self._pil_image_to_base64(image)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            response = self.model.invoke([message])
            result_text = response.content.strip()
            
            print(f"Classification raw response: {result_text[:200]}...")
            
            # Parse the response
            image_type = "unclear"
            is_diagnostic = False
            intent = ""
            confidence = 0.5
            
            lines = result_text.split("\n")
            for line in lines:
                line_lower = line.lower().strip()
                if line_lower.startswith("type:"):
                    type_value = line.split(":", 1)[1].strip().lower()
                    # Handle variations in response
                    if "document" in type_value:
                        image_type = "document"
                    elif "medical" in type_value:
                        image_type = "medical"
                    elif "general" in type_value:
                        image_type = "general"
                    elif type_value in ["medical", "document", "general", "unclear"]:
                        image_type = type_value
                elif line_lower.startswith("diagnostic:"):
                    diag_value = line.split(":", 1)[1].strip().lower()
                    is_diagnostic = diag_value in ["yes", "true", "1"]
                elif line_lower.startswith("purpose:"):
                    intent = line.split(":", 1)[1].strip()
                elif line_lower.startswith("confidence:"):
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
                    print("Fallback: Detected document keywords in response, changing type to document")
                    image_type = "document"
            
            # Force correct diagnostic status based on image type
            # Only medical images can be diagnostic
            if image_type == "medical":
                is_diagnostic = True
            elif image_type in ["document", "general"]:
                # Documents and general images are NOT for medical diagnosis
                is_diagnostic = False
            # For unclear, keep whatever LLM returned
            
            print(f"Image classification: type={image_type}, diagnostic={is_diagnostic}, confidence={confidence}")
            
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
            
            context_hint = f"\n**User Request:** {user_input}" if user_input else ""
            
            prompt = f"""You are a medical document reading and information extraction expert. Please analyze this document image in DETAIL.
{context_hint}

**IMPORTANT - Your Task:**
1. **Identify Document Type**: Prescription, test results, medical exam form, or other?

2. **If PRESCRIPTION - Extract EACH MEDICATION with this format:**
   - Medication Name: [full name]
   - Dosage: [amount, mg/ml if present]
   - Instructions: [times per day, oral/topical/injection...]
   - Timing: [before/after meals, morning/afternoon/evening]
   - Quantity: [number of pills/bottles/...]

3. **If TEST RESULTS - Extract each test value:**
   - Test Name: [name]
   - Result: [value]
   - Unit: [measurement unit]
   - Normal Range: [if available]

4. **Additional Information:**
   - Patient Name (if present)
   - Doctor/Clinic Name (if present)
   - Prescription/Test Date (if present)
   - Diagnosis/Notes (if present)

**Important:**
- Extract ALL readable information
- Mark "[unreadable]" for unclear/blurry sections
- NO medical advice or diagnosis
- Be DETAILED and SPECIFIC

**Document Analysis:**"""
            
            image_base64 = self._pil_image_to_base64(image)
            
            print(f"Sending document to LLM for analysis...")
            print(f"Image base64 length: {len(image_base64)} chars")
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            )
            
            try:
                response = self.llm.invoke(messages)
                print(f"Raw response type: {type(response)}")
                print(f"Raw response: {response}")
                
                if hasattr(response, 'content'):
                    content = response.content.strip() if response.content else ""
                else:
                    content = str(response).strip()
                    
            except Exception as invoke_error:
                print(f"ERROR: LLM invoke error: {invoke_error}")
                import traceback
                traceback.print_exc()
                content = ""
            
            print(f"Document analysis response length: {len(content)} chars")
            if content:
                print(f"Document analysis preview: {content[:300]}...")
            else:
                print("WARNING: Document analysis returned empty content!")
            
            # Try to detect document type from response
            doc_type = "unknown"
            content_lower = content.lower()
            if "đơn thuốc" in content_lower or "prescription" in content_lower:
                doc_type = "prescription"
            elif "xét nghiệm" in content_lower or "kết quả" in content_lower or "test" in content_lower:
                doc_type = "test_result"
            elif "exam" in content_lower or "record" in content_lower:
                doc_type = "medical_record"
            elif "invoice" in content_lower or "bill" in content_lower:
                doc_type = "invoice"
            
            return {
                "description": "Medical document analysis",
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