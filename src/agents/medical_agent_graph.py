"""LangGraph multi-agent system for medical image analysis"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict, Any
import operator
import os
import logging
import google.generativeai as genai
from src.vision.gemini_vision_analyzer import GeminiVisionAnalyzer

logger = logging.getLogger(__name__)


# Define agent state (shared between all agents)
class MedicalAnalysisState(TypedDict):
    """
    Shared state that flows through the agent graph.
    Each agent reads from and writes to this state.
    """
    image_data: str
    symptoms_text: str
    visual_analysis: Dict[str, Any]
    medical_assessment: str
    risk_level: str
    recommendations: List[str]
    confidence_score: float
    messages: Annotated[List[str], operator.add]  # Append-only log


class MedicalAgentGraph:
    """
    Multi-agent system for medical image analysis using LangGraph.
    
    Agent Flow:
    1. Vision Agent: Analyzes image with Hugging Face models (BLIP-2, VQA)
    2. Symptom Matcher: Combines visual findings with text symptoms (Gemini)
    3. Risk Assessor: Determines urgency level (Gemini)
    4. Recommender: Provides actionable next steps (Gemini)
    
    All agents work collaboratively, passing state through the graph.
    """
    
    def __init__(self, google_api_key: str, hf_token: str = None):
        """
        Initialize the multi-agent system.
        
        Args:
            google_api_key: Google API key for Gemini
            hf_token: Not used anymore (kept for compatibility)
        """
        self.google_api_key = google_api_key
        
        # Initialize vision analyzer (Gemini Vision)
        self.vision_analyzer = GeminiVisionAnalyzer(google_api_key)
        
        # Initialize Gemini for text reasoning
        genai.configure(api_key=google_api_key)
        self.gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            generation_config={
                "temperature": 0.3,  # Lower = more consistent
                "top_p": 0.95,
                "top_k": 40,
            }
        )
        
        # Build the agent graph
        self.graph = self._build_graph()
        
        logger.info("MedicalAgentGraph initialized with 4 agents")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Graph structure:
        START → Vision Agent → Symptom Matcher → Risk Assessor → Recommender → END
        """
        workflow = StateGraph(MedicalAnalysisState)
        
        # Create wrapper functions (LangGraph needs plain functions, not bound methods)
        def vision_wrapper(state):
            return self.vision_agent(state)
        
        def symptom_matcher_wrapper(state):
            return self.symptom_matcher_agent(state)
        
        def risk_assessor_wrapper(state):
            return self.risk_assessor_agent(state)
        
        def recommender_wrapper(state):
            return self.recommender_agent(state)
        
        # Add nodes (agents) - use wrapper functions
        workflow.add_node("vision_agent", vision_wrapper)
        workflow.add_node("symptom_matcher", symptom_matcher_wrapper)
        workflow.add_node("risk_assessor", risk_assessor_wrapper)
        workflow.add_node("recommender", recommender_wrapper)
        
        # Define edges (workflow sequence)
        workflow.set_entry_point("vision_agent")
        workflow.add_edge("vision_agent", "symptom_matcher")
        workflow.add_edge("symptom_matcher", "risk_assessor")
        workflow.add_edge("risk_assessor", "recommender")
        workflow.add_edge("recommender", END)
        
        # Compile the graph
        return workflow.compile()
    
    def vision_agent(self, state: MedicalAnalysisState) -> MedicalAnalysisState:
        """
        Agent 1: Analyze image using Hugging Face vision models.
        
        This agent:
        - Processes the uploaded image
        - Generates visual description (BLIP-2)
        - Answers specific questions about the image (BLIP-VQA)
        - Updates state with visual analysis results
        """
        logger.info("🔍 Vision Agent: Starting image analysis...")
        
        try:
            # Analyze image with HF models (synchronous call)
            visual_analysis = self.vision_analyzer.analyze_image(
                state["image_data"],
                state.get("symptoms_text")
            )
            
            # Update state
            state["visual_analysis"] = visual_analysis
            state["confidence_score"] = visual_analysis["confidence"]
            
            # Log progress
            desc = visual_analysis["visual_description"][:80]
            state["messages"].append(
                f"✅ Vision Agent: Analysis complete ({desc}...)"
            )
            
            if visual_analysis.get("error"):
                logger.warning(f"Vision analysis had errors: {visual_analysis['error']}")
        
        except Exception as e:
            logger.error(f"Vision Agent error: {str(e)}")
            state["visual_analysis"] = {
                "visual_description": "",
                "visual_qa_results": {},
                "confidence": 0.0,
                "error": str(e)
            }
            state["messages"].append(f"❌ Vision Agent: Error - {str(e)}")
        
        return state
    
    def symptom_matcher_agent(self, state: MedicalAnalysisState) -> MedicalAnalysisState:
        """
        Agent 2: Match visual findings with text symptoms using Gemini.
        
        This agent:
        - Reviews visual analysis from Agent 1
        - Combines with patient's text description
        - Provides preliminary medical assessment
        - Identifies patterns and correlations
        """
        logger.info("🩺 Symptom Matcher: Correlating visual + text symptoms...")
        
        try:
            visual = state["visual_analysis"]
            
            # Build prompt for Gemini
            prompt = f"""Bạn là trợ lý y tế chuyên nghiệp. Nhiệm vụ của bạn là kết hợp thông tin hình ảnh với triệu chứng của bệnh nhân.

            **Phân tích hình ảnh:**
            - Mô tả: {visual.get('visual_description', 'Không có')}
            - Kết quả Q&A: {visual.get('visual_qa_results', {})}

            **Triệu chứng của bệnh nhân:**
            {state.get('symptoms_text', 'Không cung cấp')}

            **Nhiệm vụ:** Viết đánh giá sơ bộ kết hợp cả hai nguồn thông tin.
            Tập trung vào:
            1. Những gì hình ảnh cho thấy
            2. Mối liên hệ với triệu chứng mô tả
            3. Các dấu hiệu đáng lo ngại (nếu có)

            **Đánh giá (3-4 câu, tiếng Việt):**"""

            # Call Gemini (synchronously)
            response = self._call_gemini_sync(prompt)
            
            # Update state
            state["medical_assessment"] = response
            state["messages"].append("✅ Symptom Matcher: Assessment complete")
            
            logger.info(f"Assessment: {response[:100]}...")
        
        except Exception as e:
            logger.error(f"Symptom Matcher error: {str(e)}")
            state["medical_assessment"] = f"Lỗi khi đánh giá: {str(e)}"
            state["messages"].append(f"❌ Symptom Matcher: Error - {str(e)}")
        
        return state
    
    def risk_assessor_agent(self, state: MedicalAnalysisState) -> MedicalAnalysisState:
        """
        Agent 3: Assess urgency/risk level using Gemini.
        
        This agent:
        - Reviews medical assessment from Agent 2
        - Determines urgency level (LOW/MEDIUM/HIGH/CRITICAL)
        - Considers severity, symptoms, visual findings
        """
        logger.info("⚠️  Risk Assessor: Determining urgency level...")
        
        try:
            # Build prompt
            prompt = f"""Bạn là chuyên gia đánh giá rủi ro y tế.

            **Đánh giá:**
            {state['medical_assessment']}

            **Nhiệm vụ:** Xác định mức độ khẩn cấp dựa trên các phát hiện.

            **Các mức độ:**
            - LOW: Vấn đề nhỏ, có thể đợi cuộc hẹn thường
            - MEDIUM: Nên gặp bác sĩ trong vài ngày
            - HIGH: Nên gặp bác sĩ trong 24 giờ
            - CRITICAL: Cần chăm sóc y tế khẩn cấp ngay (cấp cứu)

            **Chỉ trả lời MỘT từ (LOW, MEDIUM, HIGH hoặc CRITICAL):**"""

            # Call Gemini (synchronously)
            response = self._call_gemini_sync(prompt)
            risk_level = response.strip().upper()
            
            # Validate risk level
            valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if risk_level not in valid_levels:
                # Try to extract from response
                for level in valid_levels:
                    if level in risk_level:
                        risk_level = level
                        break
                else:
                    risk_level = "MEDIUM"  # Default
            
            # Update state
            state["risk_level"] = risk_level
            state["messages"].append(f"✅ Risk Assessor: Level = {risk_level}")
            
            logger.info(f"Risk level: {risk_level}")
        
        except Exception as e:
            logger.error(f"Risk Assessor error: {str(e)}")
            state["risk_level"] = "MEDIUM"  # Safe default
            state["messages"].append(f"❌ Risk Assessor: Error - {str(e)}")
        
        return state
    
    def recommender_agent(self, state: MedicalAnalysisState) -> MedicalAnalysisState:
        """
        Agent 4: Generate recommendations using Gemini.
        
        This agent:
        - Reviews all previous analysis
        - Provides actionable recommendations
        - Tailors advice to risk level
        - Suggests next steps
        """
        logger.info("💡 Recommender: Generating recommendations...")
        
        try:
            # Build prompt based on risk level
            risk_context = {
                "LOW": "Đây là vấn đề nhỏ. Tập trung vào tự chăm sóc và theo dõi.",
                "MEDIUM": "Nên tư vấn bác sĩ sớm. Cung cấp lời khuyên chăm sóc tại nhà trong khi chờ.",
                "HIGH": "Cần gặp bác sĩ trong 24 giờ. Nhấn mạnh tầm quan trọng của việc tìm kiếm chăm sóc.",
                "CRITICAL": "KHẨN CẤP! Cần chăm sóc y tế ngay lập tức. Hướng dẫn đến cấp cứu."
            }
            
            prompt = f"""Bạn là cố vấn y tế. Cung cấp khuyến nghị cho bệnh nhân.

            **Đánh giá:**
            {state['medical_assessment']}

            **Mức độ rủi ro:** {state['risk_level']}
            **Ngữ cảnh:** {risk_context.get(state['risk_level'], '')}

            **Nhiệm vụ:** Viết 3-5 khuyến nghị cụ thể cho bệnh nhân.

            Bao gồm:
            1. Hành động ngay lập tức (nếu có)
            2. Khi nào cần gặp bác sĩ
            3. Lời khuyên chăm sóc tại nhà (nếu phù hợp)
            4. Đề xuất theo dõi

            **Định dạng:** Danh sách đánh số (1., 2., 3., ...)
            **Ngôn ngữ:** Tiếng Việt, rõ ràng, dễ hiểu

            **Khuyến nghị:**"""

            # Call Gemini (synchronously)
            response = self._call_gemini_sync(prompt)
            
            # Parse recommendations (numbered list)
            recommendations = []
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 3:
                    # Check if starts with number
                    if line[0].isdigit() or line.startswith('-') or line.startswith('•'):
                        # Remove number/bullet
                        clean_line = line.lstrip('0123456789.-•) ').strip()
                        if clean_line:
                            recommendations.append(clean_line)
            
            # Fallback if parsing failed
            if not recommendations:
                recommendations = [response]
            
            # Update state
            state["recommendations"] = recommendations
            state["messages"].append(
                f"✅ Recommender: Generated {len(recommendations)} recommendations"
            )
            
            logger.info(f"Generated {len(recommendations)} recommendations")
        
        except Exception as e:
            logger.error(f"Recommender error: {str(e)}")
            state["recommendations"] = [
                "Vui lòng tham khảo ý kiến bác sĩ để được đánh giá chuyên nghiệp.",
                "Theo dõi các triệu chứng và ghi lại bất kỳ thay đổi nào.",
                "Nếu tình trạng xấu đi, hãy tìm kiếm chăm sóc y tế ngay lập tức."
            ]
            state["messages"].append(f"❌ Recommender: Error - {str(e)}")
        
        return state
    
    def _call_gemini_sync(self, prompt: str) -> str:
        """
        Synchronous helper method to call Gemini API.
        
        Args:
            prompt: Text prompt for Gemini
        
        Returns:
            Generated text response
        """
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    async def _call_gemini(self, prompt: str) -> str:
        """
        Helper method to call Gemini API.
        
        Args:
            prompt: Text prompt for Gemini
        
        Returns:
            Generated text response
        """
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def analyze(
        self, 
        image_data: str, 
        symptoms_text: str = ""
    ) -> Dict[str, Any]:
        """
        Run the complete multi-agent analysis pipeline.
        
        Args:
            image_data: Base64 encoded image
            symptoms_text: User's description of symptoms
        
        Returns:
            Complete analysis with all agent outputs:
            {
                "visual_analysis": {...},
                "medical_assessment": "...",
                "risk_level": "MEDIUM",
                "recommendations": ["...", "..."],
                "confidence_score": 0.85,
                "workflow_messages": ["...", "..."]
            }
        """
        logger.info("🚀 Starting multi-agent medical analysis...")
        
        # Initialize state
        initial_state = MedicalAnalysisState(
            image_data=image_data,
            symptoms_text=symptoms_text,
            visual_analysis={},
            medical_assessment="",
            risk_level="",
            recommendations=[],
            confidence_score=0.0,
            messages=[]
        )
        
        try:
            # Run the agent graph (synchronous)
            final_state = self.graph.invoke(initial_state)
            
            logger.info("✅ Multi-agent analysis complete!")
            
            return {
                "visual_analysis": final_state["visual_analysis"],
                "medical_assessment": final_state["medical_assessment"],
                "risk_level": final_state["risk_level"],
                "recommendations": final_state["recommendations"],
                "confidence_score": final_state["confidence_score"],
                "workflow_messages": final_state["messages"]
            }
        
        except Exception as e:
            logger.error(f"Multi-agent analysis failed: {str(e)}")
            raise


# Test function
def test_agent_graph():
    """Test the multi-agent system"""
    import base64
    from io import BytesIO
    from PIL import Image
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("🧪 Testing Medical Agent Graph...\n")
    
    # Create test image
    print("📸 Creating test image...")
    img = Image.new('RGB', (300, 300), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    image_data = f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    
    # Initialize agent graph
    print("🤖 Initializing agents...")
    agent_graph = MedicalAgentGraph(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        hf_token=os.getenv("HUGGINGFACE_TOKEN")
    )
    
    # Run analysis
    print("\n🔄 Running multi-agent analysis...\n")
    result = agent_graph.analyze(
        image_data=image_data,
        symptoms_text="Tôi có vết đỏ trên cánh tay và hơi ngứa"
    )
    
    # Print results
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n🔍 Visual Description:")
    print(f"  {result['visual_analysis']['visual_description']}")
    
    print(f"\n🩺 Medical Assessment:")
    print(f"  {result['medical_assessment']}")
    
    print(f"\n⚠️  Risk Level: {result['risk_level']}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📈 Confidence: {result['confidence_score']:.0%}")
    
    print(f"\n📝 Workflow Log:")
    for msg in result['workflow_messages']:
        print(f"  {msg}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_agent_graph()
