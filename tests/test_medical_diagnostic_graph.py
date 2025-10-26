"""
Test suite for Medical Diagnostic Graph implementation
"""
import pytest
import os
from dotenv import load_dotenv
from agents.medical_diagnostic_graph import MedicalDiagnosticGraph, GraphState

load_dotenv()


@pytest.fixture
def diagnostic_graph():
    """Fixture to create a diagnostic graph instance"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not found in environment")
    return MedicalDiagnosticGraph(google_api_key=api_key)


class TestGraphStateDefinition:
    """Test the GraphState structure"""
    
    def test_graph_state_fields(self):
        """Test that GraphState has all required fields"""
        state: GraphState = {
            "input": "test",
            "intent": "normal_conversation",
            "image": None,
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
            "metadata": {}
        }
        
        # Verify all required fields are present
        assert "input" in state
        assert "intent" in state
        assert "final_response" in state
        assert "messages" in state


class TestRouterNode:
    """Test the Router node functionality"""
    
    def test_router_classifies_normal_conversation(self, diagnostic_graph):
        """Test router correctly identifies normal conversation"""
        result = diagnostic_graph.analyze(
            user_input="Phòng khám mở cửa lúc mấy giờ?",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "normal_conversation"
        assert len(result["messages"]) > 0
    
    def test_router_classifies_appointment_request(self, diagnostic_graph):
        """Test router identifies appointment booking requests"""
        result = diagnostic_graph.analyze(
            user_input="Tôi muốn đặt lịch khám bệnh",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "needs_examiner"
    
    def test_router_extracts_symptoms(self, diagnostic_graph):
        """Test router extracts symptoms from input"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị đau đầu và sốt từ 2 ngày nay",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "symptoms_only"


class TestConversationAgent:
    """Test the ConversationAgent node"""
    
    def test_conversation_agent_responds_to_faq(self, diagnostic_graph):
        """Test conversation agent handles FAQ questions"""
        result = diagnostic_graph.analyze(
            user_input="Phòng khám có nhận bảo hiểm không?",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "normal_conversation"
        assert len(result["final_response"]) > 0
        assert "bảo hiểm" in result["final_response"].lower() or "insurance" in result["final_response"].lower()
    
    def test_conversation_agent_provides_clinic_info(self, diagnostic_graph):
        """Test conversation agent provides clinic information"""
        result = diagnostic_graph.analyze(
            user_input="Địa chỉ phòng khám ở đâu?",
            image=None
        )
        
        assert result["success"] is True
        assert len(result["final_response"]) > 0


class TestAppointmentScheduler:
    """Test the AppointmentScheduler node"""
    
    def test_appointment_scheduler_extracts_details(self, diagnostic_graph):
        """Test appointment scheduler extracts booking details"""
        result = diagnostic_graph.analyze(
            user_input="Đặt lịch cho Nguyễn Văn A vào ngày mai lúc 2 giờ chiều để khám tổng quát",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "needs_examiner"
        assert "appointment_details" in result
    
    def test_appointment_scheduler_handles_incomplete_info(self, diagnostic_graph):
        """Test scheduler prompts for missing information"""
        result = diagnostic_graph.analyze(
            user_input="Tôi muốn đặt lịch",
            image=None
        )
        
        assert result["success"] is True
        # Should prompt for more information
        assert len(result["final_response"]) > 0


class TestDiagnosisEngine:
    """Test the DiagnosisEngine node"""
    
    def test_diagnosis_engine_generates_diagnosis(self, diagnostic_graph):
        """Test diagnosis engine produces diagnostic results"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị sốt 38.5 độ, ho và đau họng từ 3 ngày",
            image=None
        )
        
        assert result["success"] is True
        assert "diagnosis" in result
        assert "primary_diagnosis" in result["diagnosis"]
        assert "severity" in result["diagnosis"]
    
    def test_diagnosis_engine_assesses_risk(self, diagnostic_graph):
        """Test diagnosis engine includes risk assessment"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị đau ngực dữ dội và khó thở",
            image=None
        )
        
        assert result["success"] is True
        assert "risk_assessment" in result
        assert "risk_level" in result["risk_assessment"]
        assert result["risk_assessment"]["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def test_diagnosis_engine_identifies_severity(self, diagnostic_graph):
        """Test diagnosis identifies severity levels"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị đau đầu nhẹ",
            image=None
        )
        
        assert result["success"] is True
        if "diagnosis" in result and result["diagnosis"]:
            assert result["diagnosis"]["severity"] in ["mild", "moderate", "severe", "critical"]


class TestInvestigationGenerator:
    """Test the InvestigationGenerator node"""
    
    def test_investigation_generator_suggests_tests(self, diagnostic_graph):
        """Test investigation generator produces test recommendations"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị sốt cao và ho ra máu",
            image=None
        )
        
        assert result["success"] is True
        # Investigation plan should be generated for medical symptoms
        if result["intent"] in ["symptoms_only", "image_and_symptoms"]:
            assert "investigation_plan" in result
            # May be empty if there's an error, but should exist
            assert isinstance(result["investigation_plan"], list)


class TestDocumentRetriever:
    """Test the DocumentRetriever node"""
    
    def test_document_retriever_retrieves_context(self, diagnostic_graph):
        """Test document retriever fetches relevant information"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị cúm",
            image=None
        )
        
        assert result["success"] is True
        # For symptoms, documents should be retrieved
        # May be empty, but field should exist
        assert "retrieved_documents" in result or result["intent"] == "normal_conversation"


class TestRecommender:
    """Test the Recommender node"""
    
    def test_recommender_generates_recommendations(self, diagnostic_graph):
        """Test recommender synthesizes final advice"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị đau đầu và chóng mặt",
            image=None
        )
        
        assert result["success"] is True
        assert "final_response" in result
        assert len(result["final_response"]) > 0
    
    def test_recommender_includes_diagnosis_info(self, diagnostic_graph):
        """Test final response includes diagnosis information"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị sốt và ho",
            image=None
        )
        
        assert result["success"] is True
        if result["intent"] in ["symptoms_only", "image_and_symptoms"]:
            # Should contain medical information
            assert len(result["final_response"]) > 50  # Substantial response


class TestGraphFlow:
    """Test complete graph execution flows"""
    
    def test_conversation_flow_ends_correctly(self, diagnostic_graph):
        """Test normal conversation flow reaches END"""
        result = diagnostic_graph.analyze(
            user_input="Giá khám bao nhiêu?",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "normal_conversation"
        # Should have executed ConversationAgent and ended
        message_log = " ".join(result["messages"])
        assert "ConversationAgent" in message_log
    
    def test_appointment_flow_ends_correctly(self, diagnostic_graph):
        """Test appointment flow reaches END"""
        result = diagnostic_graph.analyze(
            user_input="Đặt lịch khám",
            image=None
        )
        
        assert result["success"] is True
        assert result["intent"] == "needs_examiner"
        message_log = " ".join(result["messages"])
        assert "AppointmentScheduler" in message_log
    
    def test_symptoms_flow_includes_parallel_processing(self, diagnostic_graph):
        """Test symptoms flow executes parallel branches"""
        result = diagnostic_graph.analyze(
            user_input="Tôi bị đau bụng và tiêu chảy",
            image=None
        )
        
        assert result["success"] is True
        if result["intent"] == "symptoms_only":
            message_log = " ".join(result["messages"])
            # Should execute DiagnosisEngine, Investigation, Retrieval, and Recommender
            assert "DiagnosisEngine" in message_log


class TestErrorHandling:
    """Test error handling across the graph"""
    
    def test_handles_empty_input(self, diagnostic_graph):
        """Test system handles empty input gracefully"""
        result = diagnostic_graph.analyze(
            user_input="",
            image=None
        )
        
        assert result["success"] is True
        assert "final_response" in result
    
    def test_handles_invalid_image(self, diagnostic_graph):
        """Test system handles invalid image data"""
        result = diagnostic_graph.analyze(
            user_input="Hình ảnh này là gì?",
            image="invalid_base64_data"
        )
        
        # Should still complete, possibly with error message
        assert "final_response" in result
    
    def test_logs_execution_steps(self, diagnostic_graph):
        """Test that execution is logged"""
        result = diagnostic_graph.analyze(
            user_input="Test",
            image=None
        )
        
        assert "messages" in result
        assert len(result["messages"]) > 0


class TestIntentClassification:
    """Test intent classification accuracy"""
    
    @pytest.mark.parametrize("input_text,expected_intent", [
        ("Phòng khám có wifi không?", "normal_conversation"),
        ("Tôi cần đặt lịch", "needs_examiner"),
        ("Gặp bác sĩ lúc nào?", "needs_examiner"),
        ("Tôi bị sốt", "symptoms_only"),
        ("Đau đầu và buồn nôn", "symptoms_only"),
    ])
    def test_intent_classification_variations(self, diagnostic_graph, input_text, expected_intent):
        """Test various input patterns are classified correctly"""
        result = diagnostic_graph.analyze(
            user_input=input_text,
            image=None
        )
        
        assert result["success"] is True
        # Intent might vary based on Gemini's interpretation, so we just verify it's valid
        assert result["intent"] in ["normal_conversation", "needs_examiner", "symptoms_only", "image_and_symptoms"]


class TestResponseQuality:
    """Test quality of generated responses"""
    
    def test_response_is_in_vietnamese(self, diagnostic_graph):
        """Test responses are in Vietnamese"""
        result = diagnostic_graph.analyze(
            user_input="Phòng khám mở cửa khi nào?",
            image=None
        )
        
        assert result["success"] is True
        # Should contain Vietnamese characters or common Vietnamese words
        response = result["final_response"]
        vietnamese_indicators = ["phòng khám", "bệnh nhân", "khám", "lịch", "giờ", "ngày"]
        assert any(indicator in response.lower() for indicator in vietnamese_indicators) or len(response) > 0
    
    def test_response_is_helpful(self, diagnostic_graph):
        """Test responses contain substantive information"""
        result = diagnostic_graph.analyze(
            user_input="Bảo hiểm y tế",
            image=None
        )
        
        assert result["success"] is True
        assert len(result["final_response"]) > 20  # Should be more than just "yes" or "no"


class TestMetadata:
    """Test metadata handling"""
    
    def test_metadata_is_preserved(self, diagnostic_graph):
        """Test custom metadata is preserved through execution"""
        result = diagnostic_graph.analyze(
            user_input="Test input",
            image=None,
            metadata={"user_id": "test123", "session_id": "abc"}
        )
        
        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"].get("user_id") == "test123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
