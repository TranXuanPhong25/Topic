"""
LangGraph-based Medical Diagnostic System
Implements the complete diagnostic flow with routing, diagnosis, risk assessment, and recommendations.
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
import operator
import logging
import google.generativeai as genai
from vision.gemini_vision_analyzer import GeminiVisionAnalyzer
from knowledge_base import FAQKnowledgeBase
from handlers.appointment import AppointmentHandler
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)


# ============================================================================
# GRAPH STATE DEFINITION (As specified in requirements)
# ============================================================================

class GraphState(TypedDict):
    """
    Comprehensive state for the medical AI system graph.
    All data flows through this shared state according to the diagram.
    """
    # Input and routing
    input: str  # Initial user query
    intent: str  # normal_conversation, needs_examiner, symptoms_only, image_and_symptoms
    
    # Image and symptoms
    image: Optional[str]  # Base64 encoded image
    symptoms: str  # Extracted symptoms from input
    
    # Vision analysis
    image_analysis_result: Dict[str, Any]  # Output from ImageAnalyzer
    
    # Combined analysis
    combined_analysis: str  # Merged symptoms and image analysis
    
    # Diagnosis and risk
    diagnosis: Dict[str, Any]  # Output from DiagnosisEngine
    risk_assessment: Dict[str, Any]  # Output from RiskAssessor
    
    # Investigation and retrieval
    investigation_plan: List[Dict[str, Any]]  # Generated list of investigations
    retrieved_documents: List[Dict[str, Any]]  # Context from Vector DB and KG
    
    # Recommendations
    recommendation: str  # Final actionable advice
    
    # Conversation and appointment
    conversation_output: str  # Result from ConversationAgent
    appointment_details: Dict[str, Any]  # Result from AppointmentScheduler
    
    # Final output
    final_response: str  # Message to be sent to user
    
    # Logging and metadata
    messages: Annotated[List[str], operator.add]  # Append-only log
    metadata: Dict[str, Any]  # Additional context


# ============================================================================
# MEDICAL DIAGNOSTIC GRAPH - Main Implementation
# ============================================================================

class MedicalDiagnosticGraph:
    """
    Comprehensive medical diagnostic system using LangGraph.
    
    Flow:
    1. Router: Classifies intent and extracts symptoms/image
    2. Conditional branching:
       - normal_conversation → ConversationAgent → END
       - needs_examiner → AppointmentScheduler → END
       - image_and_symptoms → ImageAnalyzer → CombineAnalysis → DiagnosisEngine
       - symptoms_only → DiagnosisEngine
    3. DiagnosisEngine (includes internal RiskAssessor)
    4. Parallel: InvestigationGenerator + DocumentRetriever
    5. Recommender (joins both paths) → END
    """
    
    def __init__(self, google_api_key: str):
        """
        Initialize the medical diagnostic system.
        
        Args:
            google_api_key: Google API key for Gemini
        """
        self.google_api_key = google_api_key
        
        # Initialize components
        self.vision_analyzer = GeminiVisionAnalyzer(google_api_key)
        self.knowledge_base = FAQKnowledgeBase()
        self.appointment_handler = AppointmentHandler()
        
        # Initialize Gemini for text reasoning
        genai.configure(api_key=google_api_key)
        self.gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("MedicalDiagnosticGraph initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow according to the diagram.
        
        Graph structure:
        Router (entry) → Conditional branching:
          - ConversationAgent → END
          - AppointmentScheduler → END
          - ImageAnalyzer → CombineAnalysis → DiagnosisEngine → [InvestigationGenerator, DocumentRetriever] → Recommender → END
          - DiagnosisEngine → [InvestigationGenerator, DocumentRetriever] → Recommender → END
        """
        workflow = StateGraph(GraphState)
        
        # Add all nodes (agents/processors)
        workflow.add_node("router", self._router_node)
        workflow.add_node("conversation_agent", self._conversation_agent_node)
        workflow.add_node("appointment_scheduler", self._appointment_scheduler_node)
        workflow.add_node("image_analyzer", self._image_analyzer_node)
        workflow.add_node("combine_analysis", self._combine_analysis_node)
        workflow.add_node("diagnosis_engine", self._diagnosis_engine_node)
        workflow.add_node("investigation_generator", self._investigation_generator_node)
        workflow.add_node("document_retriever", self._document_retriever_node)
        workflow.add_node("recommender", self._recommender_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Conditional edges from Router
        workflow.add_conditional_edges(
            "router",
            self._route_based_on_intent,
            {
                "normal_conversation": "conversation_agent",
                "needs_examiner": "appointment_scheduler",
                "image_and_symptoms": "image_analyzer",
                "symptoms_only": "diagnosis_engine",
            }
        )
        
        # Linear edges for image analysis path
        workflow.add_edge("image_analyzer", "combine_analysis")
        workflow.add_edge("combine_analysis", "diagnosis_engine")
        
        # Sequential edges from DiagnosisEngine (to avoid concurrent state updates)
        # First generate investigations, then retrieve documents, then recommend
        workflow.add_edge("diagnosis_engine", "investigation_generator")
        workflow.add_edge("investigation_generator", "document_retriever")
        workflow.add_edge("document_retriever", "recommender")
        
        # End points
        workflow.add_edge("conversation_agent", END)
        workflow.add_edge("appointment_scheduler", END)
        workflow.add_edge("recommender", END)
        
        # Compile the graph
        return workflow.compile()
    
    # ========================================================================
    # ROUTING FUNCTION
    # ========================================================================
    
    def _route_based_on_intent(self, state: GraphState) -> Literal["normal_conversation", "needs_examiner", "image_and_symptoms", "symptoms_only"]:
        """
        Route to appropriate node based on classified intent.
        """
        intent = state.get("intent", "normal_conversation")
        logger.info(f"Routing to: {intent}")
        return intent
    
    # ========================================================================
    # NODE IMPLEMENTATIONS
    # ========================================================================
    
    def _router_node(self, state: GraphState) -> GraphState:
        """
        Router Node: Classifies intent and extracts symptoms/image.
        
        Logic:
        1. Analyze user input
        2. Determine intent (conversation, examiner, symptoms, image+symptoms)
        3. Extract symptoms if present
        4. Extract image if present
        """
        # Check if router has already run (avoid duplicate executions)
        if state.get("intent") and state.get("intent") != "":
            logger.info("🔀 Router: Already classified, skipping...")
            return state
        
        logger.info("🔀 Router: Classifying user intent...")
        
        user_input = state.get("input", "")
        image = state.get("image")
        
        # Initialize state fields
        state["symptoms"] = ""
        state["intent"] = "normal_conversation"
        state["metadata"] = state.get("metadata", {})
        state["messages"] = state.get("messages", [])
        
        try:
            # Use Gemini to classify intent and extract symptoms
            classification_prompt = f"""Phân tích đầu vào của người dùng và trả về JSON với các trường sau:

                                        Input: "{user_input}"
                                        Có hình ảnh: {"Có" if image else "Không"}

                                        Xác định:
                                        1. intent: "normal_conversation" (hỏi thông tin phòng khám, giá cả, FAQ), 
                                                "needs_examiner" (muốn đặt lịch khám hoặc cần gặp bác sĩ), 
                                                "symptoms_only" (mô tả triệu chứng không có hình ảnh), 
                                                "image_and_symptoms" (có hình ảnh y khoa và triệu chứng)
                                        2. symptoms: chuỗi triệu chứng được trích xuất (nếu có), rỗng nếu không

                                        Chỉ trả về JSON, không có văn bản bổ sung:
                                        {{"intent": "...", "symptoms": "..."}}"""

            response = self.gemini_model.generate_content(classification_prompt)
            result_text = response.text.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            intent = result.get("intent", "normal_conversation")
            symptoms = result.get("symptoms", "")
            
            # Override intent if image is present and symptoms detected
            if image and symptoms:
                intent = "image_and_symptoms"
            elif not image and symptoms:
                intent = "symptoms_only"
            
            state["intent"] = intent
            state["symptoms"] = symptoms
            state["messages"].append(f"✅ Router: Intent classified as '{intent}'")
            
            if symptoms:
                state["messages"].append(f"✅ Router: Extracted symptoms: {symptoms[:100]}...")
            
            logger.info(f"Intent: {intent}, Symptoms: {symptoms[:50]}...")
            
        except Exception as e:
            logger.error(f"Router error: {str(e)}")
            state["intent"] = "normal_conversation"
            state["messages"].append(f"❌ Router: Error - {str(e)}, defaulting to conversation")
        
        return state
    
    def _conversation_agent_node(self, state: GraphState) -> GraphState:
        """
        ConversationAgent Node: Handles normal conversations using tools.
        
        Tools: CareGuideTool, FAQTool, ClinicInfoTool, PriceTableTool
        """
        logger.info("💬 ConversationAgent: Handling conversation...")
        
        user_input = state.get("input", "")
        
        try:
            # Search knowledge base for relevant FAQ
            faq_results = self.knowledge_base.search_faqs(user_input, limit=3)
            
            # Build context from FAQ
            context = "\n\n".join([
                f"Q: {faq['question']}\nA: {faq['answer']}"
                for faq in faq_results
            ])
            
            # Use Gemini to generate response
            conversation_prompt = f"""Bạn là trợ lý y tế thân thiện cho phòng khám. Trả lời câu hỏi của bệnh nhân.

                                        Thông tin phòng khám:
                                        - Tên: {self.knowledge_base.clinic_info['name']}
                                        - Giờ làm việc: {self.knowledge_base.clinic_info['hours']}
                                        - Điện thoại: {self.knowledge_base.clinic_info['phone']}

                                        Câu hỏi thường gặp liên quan:
                                        {context}

                                        Câu hỏi của bệnh nhân: "{user_input}"

                                        Trả lời ngắn gọn, hữu ích, chuyên nghiệp (2-3 câu):"""

            response = self.gemini_model.generate_content(conversation_prompt)
            conversation_output = response.text.strip()
            
            state["conversation_output"] = conversation_output
            state["final_response"] = conversation_output
            state["messages"].append("✅ ConversationAgent: Response generated")
            
            logger.info(f"Conversation response: {conversation_output[:100]}...")
            
        except Exception as e:
            logger.error(f"ConversationAgent error: {str(e)}")
            state["conversation_output"] = "Xin lỗi, tôi đang gặp sự cố. Vui lòng gọi phòng khám để được hỗ trợ."
            state["final_response"] = state["conversation_output"]
            state["messages"].append(f"❌ ConversationAgent: Error - {str(e)}")
        
        return state
    
    def _appointment_scheduler_node(self, state: GraphState) -> GraphState:
        """
        AppointmentScheduler Node: Handles appointment booking.
        """
        logger.info("📅 AppointmentScheduler: Handling booking...")
        
        user_input = state.get("input", "")
        # TODO: notworking
        try:
            # Extract appointment details using Gemini
            extraction_prompt = f"""Trích xuất thông tin đặt lịch từ đầu vào. Trả về JSON:

            Input: "{user_input}"

            Trích xuất (nếu có):
            - patient_name: tên bệnh nhân
            - date: ngày (YYYY-MM-DD)
            - time: giờ (HH:MM)
            - reason: lý do khám

            Nếu thiếu thông tin, đặt null. Chỉ trả về JSON:
            {{"patient_name": "...", "date": "...", "time": "...", "reason": "..."}}"""

            response = self.gemini_model.generate_content(extraction_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            appointment_data = json.loads(result_text)
            
            # Check if we have enough information
            missing_fields = []
            for field in ["patient_name", "date", "time", "reason"]:
                if not appointment_data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                # Generate prompt for missing information
                missing_str = ", ".join(missing_fields)
                response_text = f"Để đặt lịch, tôi cần thêm thông tin: {missing_str}. Bạn có thể cung cấp không?"
            else:
                # Validate and create appointment (simplified - in real app, use AppointmentHandler)
                response_text = f"""Đã đặt lịch thành công!

📅 Thông tin:
- Bệnh nhân: {appointment_data['patient_name']}
- Ngày: {appointment_data['date']}
- Giờ: {appointment_data['time']}
- Lý do: {appointment_data['reason']}

Chúng tôi sẽ gửi xác nhận qua tin nhắn. Cảm ơn!"""
            
            state["appointment_details"] = appointment_data
            state["final_response"] = response_text
            state["messages"].append("✅ AppointmentScheduler: Processed")
            
            logger.info(f"Appointment: {appointment_data}")
            
        except Exception as e:
            logger.error(f"AppointmentScheduler error: {str(e)}")
            state["appointment_details"] = {}
            state["final_response"] = "Để đặt lịch, vui lòng cung cấp: tên, ngày, giờ, và lý do khám."
            state["messages"].append(f"❌ AppointmentScheduler: Error - {str(e)}")
        
        return state
    
    def _image_analyzer_node(self, state: GraphState) -> GraphState:
        """
        ImageAnalyzer Node: Analyzes image in context of symptoms.
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
    
    def _combine_analysis_node(self, state: GraphState) -> GraphState:
        """
        CombineAnalysis Node: Merges text symptoms and image analysis.
        """
        logger.info("🔗 CombineAnalysis: Merging symptoms and image analysis...")
        
        symptoms = state.get("symptoms", "")
        image_analysis = state.get("image_analysis_result", {})
        
        try:
            # Combine information
            visual_desc = image_analysis.get("visual_description", "")
            visual_qa = image_analysis.get("visual_qa_results", {})
            
            combined = f"""**Triệu chứng của bệnh nhân:**
{symptoms}

**Phân tích hình ảnh:**
Mô tả: {visual_desc}

**Kết quả Visual Q&A:**
{json.dumps(visual_qa, ensure_ascii=False, indent=2)}"""
            
            state["combined_analysis"] = combined
            state["messages"].append("✅ CombineAnalysis: Merged successfully")
            
            logger.info(f"Combined analysis length: {len(combined)} characters")
            
        except Exception as e:
            logger.error(f"CombineAnalysis error: {str(e)}")
            state["combined_analysis"] = symptoms  # Fallback to symptoms only
            state["messages"].append(f"❌ CombineAnalysis: Error - {str(e)}")
        
        return state
    
    def _diagnosis_engine_node(self, state: GraphState) -> GraphState:
        """
        DiagnosisEngine Node: Runs core diagnostic logic with risk assessment.
        
        Input: combined_analysis (if image) or symptoms (if symptoms only)
        Internally calls RiskAssessor to refine diagnosis
        """
        logger.info("🩺 DiagnosisEngine: Running diagnostic analysis...")
        
        # Get input - use combined_analysis if available, otherwise symptoms
        analysis_input = state.get("combined_analysis") or state.get("symptoms", "")
        
        try:
            # Generate diagnosis using Gemini
            diagnosis_prompt = f"""Bạn là bác sĩ AI chuyên nghiệp. Phân tích thông tin bệnh nhân và đưa ra chẩn đoán sơ bộ.

**Thông tin bệnh nhân:**
{analysis_input}

**Nhiệm vụ:**
1. Đưa ra các chẩn đoán khả năng cao (top 2-3)
2. Mức độ nghiêm trọng
3. Các triệu chứng đáng lo ngại

Trả về JSON:
{{
    "primary_diagnosis": "Chẩn đoán chính",
    "differential_diagnoses": ["Chẩn đoán khác 1", "Chẩn đoán khác 2"],
    "severity": "mild/moderate/severe/critical",
    "concerning_symptoms": ["Triệu chứng 1", "Triệu chứng 2"],
    "explanation": "Giải thích ngắn gọn"
}}

Chỉ trả về JSON:"""

            response = self.gemini_model.generate_content(diagnosis_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            diagnosis = json.loads(result_text)
            
            # Internal risk assessment
            severity = diagnosis.get("severity", "moderate")
            risk_level = self._assess_risk_internal(severity, diagnosis)
            
            state["diagnosis"] = diagnosis
            state["risk_assessment"] = risk_level
            state["messages"].append(f"✅ DiagnosisEngine: Diagnosis complete (severity: {severity})")
            
            logger.info(f"Diagnosis: {diagnosis.get('primary_diagnosis', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"DiagnosisEngine error: {str(e)}")
            state["diagnosis"] = {
                "primary_diagnosis": "Không thể xác định",
                "differential_diagnoses": [],
                "severity": "moderate",
                "concerning_symptoms": [],
                "explanation": f"Lỗi: {str(e)}"
            }
            state["risk_assessment"] = {"risk_level": "MEDIUM", "explanation": "Mặc định do lỗi"}
            state["messages"].append(f"❌ DiagnosisEngine: Error - {str(e)}")
        
        return state
    
    def _assess_risk_internal(self, severity: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal risk assessor (called by DiagnosisEngine).
        """
        risk_mapping = {
            "mild": "LOW",
            "moderate": "MEDIUM",
            "severe": "HIGH",
            "critical": "CRITICAL"
        }
        
        risk_level = risk_mapping.get(severity.lower(), "MEDIUM")
        
        # Check for concerning symptoms
        concerning = diagnosis.get("concerning_symptoms", [])
        if len(concerning) >= 3 and risk_level == "MEDIUM":
            risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "explanation": f"Dựa trên mức độ nghiêm trọng: {severity}",
            "requires_immediate_attention": risk_level in ["HIGH", "CRITICAL"]
        }
    
    def _investigation_generator_node(self, state: GraphState) -> GraphState:
        """
        InvestigationGenerator Node: Generates potential follow-up tests.
        """
        logger.info("🔬 InvestigationGenerator: Generating investigation plan...")
        
        diagnosis = state.get("diagnosis", {})
        
        try:
            # Generate investigation plan using Gemini
            investigation_prompt = f"""Dựa trên chẩn đoán, đề xuất các xét nghiệm/kiểm tra cần thiết.

**Chẩn đoán:**
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

**Nhiệm vụ:** Đề xuất 3-5 xét nghiệm/kiểm tra phù hợp.

Trả về JSON array:
[
    {{"test_name": "Tên xét nghiệm", "reason": "Lý do", "priority": "high/medium/low"}},
    ...
]

Chỉ trả về JSON:"""

            response = self.gemini_model.generate_content(investigation_prompt)
            result_text = response.text.strip()
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            investigations = json.loads(result_text)
            
            state["investigation_plan"] = investigations
            state["messages"].append(f"✅ InvestigationGenerator: {len(investigations)} tests suggested")
            
            logger.info(f"Generated {len(investigations)} investigation items")
            
        except Exception as e:
            logger.error(f"InvestigationGenerator error: {str(e)}")
            state["investigation_plan"] = []
            state["messages"].append(f"❌ InvestigationGenerator: Error - {str(e)}")
        
        return state
    
    def _document_retriever_node(self, state: GraphState) -> GraphState:
        """
        DocumentRetriever Node: Performs information augmentation.
        
        Queries Vector Database (embeddings) and Knowledge Graph (KB).
        """
        logger.info("📚 DocumentRetriever: Retrieving relevant medical documents...")
        
        diagnosis = state.get("diagnosis", {})
        primary_diagnosis = diagnosis.get("primary_diagnosis", "")
        
        try:
            # Search knowledge base for relevant information
            # In real implementation, this would query vector DB + KG
            search_results = self.knowledge_base.search_faqs(primary_diagnosis, limit=5)
            
            # Format as documents
            documents = [
                {
                    "source": "FAQ Database",
                    "content": result.get("answer", ""),
                    "relevance": 0.9
                }
                for result in search_results
            ]
            
            # Add medical knowledge (simulated)
            documents.append({
                "source": "Medical Knowledge Graph",
                "content": f"Thông tin y khoa về: {primary_diagnosis}",
                "relevance": 0.8
            })
            
            state["retrieved_documents"] = documents
            state["messages"].append(f"✅ DocumentRetriever: Retrieved {len(documents)} documents")
            
            logger.info(f"Retrieved {len(documents)} relevant documents")
            
        except Exception as e:
            logger.error(f"DocumentRetriever error: {str(e)}")
            state["retrieved_documents"] = []
            state["messages"].append(f"❌ DocumentRetriever: Error - {str(e)}")
        
        return state
    
    def _recommender_node(self, state: GraphState) -> GraphState:
        """
        Recommender Node: Synthesizes investigations and retrieved context.
        
        Waits for both InvestigationGenerator and DocumentRetriever to complete.
        """
        logger.info("💡 Recommender: Generating final recommendations...")
        
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        investigation_plan = state.get("investigation_plan", [])
        retrieved_documents = state.get("retrieved_documents", [])
        
        try:
            # Build context
            context = f"""**Chẩn đoán:**
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

**Đánh giá rủi ro:**
{json.dumps(risk_assessment, ensure_ascii=False, indent=2)}

**Kế hoạch xét nghiệm:**
{json.dumps(investigation_plan, ensure_ascii=False, indent=2)}

**Tài liệu tham khảo:**
{len(retrieved_documents)} documents retrieved"""
            
            # Generate recommendations using Gemini
            recommendation_prompt = f"""Dựa trên phân tích, đưa ra khuyến nghị cuối cùng cho bệnh nhân.

{context}

**Nhiệm vụ:** Viết khuyến nghị hành động rõ ràng, dễ hiểu (3-5 câu).

Bao gồm:
1. Hành động ngay lập tức (nếu cần)
2. Khi nào cần gặp bác sĩ
3. Xét nghiệm cần làm
4. Chăm sóc tại nhà (nếu phù hợp)

**Khuyến nghị (tiếng Việt, thân thiện):**"""

            response = self.gemini_model.generate_content(recommendation_prompt)
            recommendation = response.text.strip()
            
            state["recommendation"] = recommendation
            state["final_response"] = self._format_final_response(state)
            state["messages"].append("✅ Recommender: Final recommendations generated")
            
            logger.info(f"Recommendation length: {len(recommendation)} characters")
            
        except Exception as e:
            logger.error(f"Recommender error: {str(e)}")
            state["recommendation"] = "Vui lòng gặp bác sĩ để được tư vấn chi tiết."
            state["final_response"] = state["recommendation"]
            state["messages"].append(f"❌ Recommender: Error - {str(e)}")
        
        return state
    
    def _format_final_response(self, state: GraphState) -> str:
        """
        Format the final response for the user.
        """
        diagnosis = state.get("diagnosis", {})
        risk_assessment = state.get("risk_assessment", {})
        recommendation = state.get("recommendation", "")
        
        response = f"""**🩺 Phân tích y tế:**

**Chẩn đoán sơ bộ:** {diagnosis.get('primary_diagnosis', 'Không xác định')}

**Mức độ rủi ro:** {risk_assessment.get('risk_level', 'MEDIUM')}

**💡 Khuyến nghị:**
{recommendation}

---
*Lưu ý: Đây là phân tích sơ bộ. Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để chẩn đoán chính xác.*"""
        
        return response
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def analyze(
        self,
        user_input: str,
        image: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user input and return diagnostic results.
        
        Args:
            user_input: User's text input
            image: Optional base64 encoded image
            metadata: Optional additional context
        
        Returns:
            Dictionary containing final_response and full state
        """
        logger.info(f"Starting analysis for input: {user_input[:100]}...")
        
        # Initialize state
        initial_state: GraphState = {
            "input": user_input,
            "image": image,
            "intent": "",
            "symptoms": "",
            "image_analysis_result": {},
            "combined_analysis": "",
            "diagnosis": {},
            "risk_assessment": {},
            "investigation_plan": [],
            "retrieved_documents": [],
            "recommendation": "",
            "conversation_output": "",
            "appointment_details": {},
            "final_response": "",
            "messages": [],
            "metadata": metadata or {}
        }
        
        try:
            # Execute the graph (returns final state only, not streaming)
            final_state = self.graph.invoke(initial_state)
            
            # Extract only the unique execution steps (final state messages)
            # LangGraph invoke() returns final state, but messages list accumulates all intermediate states
            # Filter to keep only one message per node
            seen_nodes = set()
            cleaned_messages = []
            
            for msg in final_state.get("messages", []):
                # Extract node name from message (e.g., "✅ Router:" -> "Router")
                if ":" in msg:
                    node_part = msg.split(":")[0].replace("✅", "").replace("❌", "").strip()
                    # Create a unique key for this message
                    msg_key = f"{node_part}:{msg.split(':')[1][:50] if ':' in msg else ''}"
                    
                    if msg_key not in seen_nodes:
                        cleaned_messages.append(msg)
                        seen_nodes.add(msg_key)
            
            return {
                "success": True,
                "final_response": final_state["final_response"],
                "intent": final_state.get("intent"),
                "diagnosis": final_state.get("diagnosis"),
                "risk_assessment": final_state.get("risk_assessment"),
                "investigation_plan": final_state.get("investigation_plan"),
                "messages": cleaned_messages,  # Use cleaned messages
                "metadata": final_state.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Graph execution error: {str(e)}")
            return {
                "success": False,
                "final_response": "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại hoặc liên hệ phòng khám.",
                "error": str(e),
                "messages": [f"❌ Graph execution error: {str(e)}"]
            }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize the graph
    graph = MedicalDiagnosticGraph(
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Example 1: Normal conversation
    print("\n" + "="*80)
    print("Example 1: Normal Conversation")
    print("="*80)
    result1 = graph.analyze("Phòng khám mở cửa lúc mấy giờ?")
    print(f"Intent: {result1['intent']}")
    print(f"Response: {result1['final_response']}")
    
    # Example 2: Appointment booking
    print("\n" + "="*80)
    print("Example 2: Appointment Booking")
    print("="*80)
    result2 = graph.analyze("Tôi muốn đặt lịch khám vào ngày mai lúc 2 giờ chiều")
    print(f"Intent: {result2['intent']}")
    print(f"Response: {result2['final_response']}")
    
    # Example 3: Symptoms only
    print("\n" + "="*80)
    print("Example 3: Symptoms Analysis")
    print("="*80)
    result3 = graph.analyze("Tôi bị đau đầu và sốt từ 2 ngày nay, nhiệt độ khoảng 38.5°C")
    print(f"Intent: {result3['intent']}")
    print(f"Response: {result3['final_response']}")
    
    print("\n" + "="*80)
    print("Graph execution complete!")
    print("="*80)
