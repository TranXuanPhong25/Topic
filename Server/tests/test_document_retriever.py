"""
Test Document Retriever Agent
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestDocumentRetrieverNode:
    """Test cases for DocumentRetrieverNode"""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM model"""
        mock = Mock()
        mock.invoke.return_value = Mock(content=json.dumps({
            "query_analysis": {
                "original_query": "test query",
                "interpreted_intent": "test intent",
                "medical_concepts": ["concept1", "concept2"]
            },
            "synthesis": {
                "main_findings": "Test findings",
                "key_points": ["point1", "point2"],
                "clinical_relevance": "Test relevance"
            },
            "confidence_assessment": {
                "overall_confidence": "high",
                "reasoning": "Test reasoning"
            },
            "limitations": ["limitation1"]
        }))
        return mock
    
    @pytest.fixture
    def mock_rag_pipeline(self):
        """Create a mock RAG pipeline"""
        mock = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "Test medical content about symptoms"
        mock_doc.metadata = {
            "title": "Medical Textbook",
            "author": "Dr. Test",
            "page": 42
        }
        
        mock.invoke.return_value = {
            "answer": "RAG generated answer",
            "english_query": "medical query",
            "context_docs": [mock_doc]
        }
        return mock
    
    @pytest.fixture
    def sample_state(self):
        """Create a sample graph state"""
        return {
            "input": "Tôi bị đau đầu và sốt",
            "chat_history": [],
            "symptoms": {
                "chief_complaint": "Đau đầu và sốt",
                "symptoms": [
                    {"name": "headache"},
                    {"name": "fever"}
                ]
            },
            "diagnosis": {
                "primary_diagnosis": "Viral infection",
                "differential_diagnoses": [
                    {"condition": "Influenza"},
                    {"condition": "COVID-19"}
                ]
            },
            "plan": [
                {
                    "agent": "document_retriever",
                    "goal": "Tìm thông tin về viral infection",
                    "context": "Patient has headache and fever",
                    "user_context": "Looking for treatment options"
                }
            ],
            "current_step": 0,
            "retrieved_documents": [],
            "rag_answer": "",
            "document_synthesis": {}
        }
    
    @patch('src.agents.document_retriever.document_retriever.RAGPipeline')
    @patch('src.agents.document_retriever.document_retriever.get_document_retriever_model')
    def test_document_retriever_initialization(self, mock_get_model, mock_rag):
        """Test that DocumentRetrieverNode initializes correctly"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        mock_get_model.return_value = Mock()
        mock_rag.from_existing_index.return_value = Mock()
        
        node = DocumentRetrieverNode()
        
        assert node.llm is not None
        assert node.pipeline is not None
    
    @patch('src.agents.document_retriever.document_retriever.RAGPipeline')
    def test_document_retriever_with_mock_llm(self, mock_rag, mock_llm, mock_rag_pipeline, sample_state):
        """Test document retriever with mocked LLM"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        mock_rag.from_existing_index.return_value = mock_rag_pipeline
        
        node = DocumentRetrieverNode(llm_model=mock_llm)
        node.pipeline = mock_rag_pipeline
        
        result_state = node(sample_state)
        
        # Check that documents were retrieved
        assert len(result_state["retrieved_documents"]) > 0
        assert result_state["rag_answer"] == "RAG generated answer"
        
        # Check that synthesis was performed
        assert result_state["document_synthesis"] is not None
        assert "query_analysis" in result_state["document_synthesis"]
        
        # Check current_step was incremented
        assert result_state["current_step"] == 1
    
    def test_build_query(self, mock_llm, sample_state):
        """Test query building from state"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None  # Disable RAG for this test
            
            query = node._build_query(sample_state)
            
            assert "Tôi bị đau đầu và sốt" in query
            assert "headache" in query or "fever" in query
    
    def test_format_symptoms(self, mock_llm):
        """Test symptoms formatting"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None
            
            symptoms = {
                "chief_complaint": "Đau đầu",
                "symptoms": [
                    {"name": "headache"},
                    {"name": "fever"}
                ]
            }
            
            formatted = node._format_symptoms(symptoms)
            
            assert "Triệu chứng" in formatted
            assert "Lý do khám" in formatted
    
    def test_format_diagnosis(self, mock_llm):
        """Test diagnosis formatting"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None
            
            diagnosis = {
                "primary_diagnosis": "Viral infection",
                "differential_diagnoses": [
                    {"condition": "Influenza"},
                    {"condition": "COVID-19"}
                ]
            }
            
            formatted = node._format_diagnosis(diagnosis)
            
            assert "Chẩn đoán chính" in formatted
            assert "Viral infection" in formatted
    
    def test_get_current_goal(self, mock_llm, sample_state):
        """Test goal extraction from plan"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None
            
            goal = node._get_current_goal(sample_state)
            
            assert goal == "Tìm thông tin về viral infection"
    
    def test_get_current_context(self, mock_llm, sample_state):
        """Test context extraction from plan"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None
            
            context = node._get_current_context(sample_state)
            
            assert context["context"] == "Patient has headache and fever"
            assert context["user_context"] == "Looking for treatment options"
    
    def test_parse_json_response(self, mock_llm):
        """Test JSON parsing from LLM response"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        with patch('src.agents.document_retriever.document_retriever.RAGPipeline'):
            node = DocumentRetrieverNode(llm_model=mock_llm)
            node.pipeline = None
            
            # Test direct JSON
            result = node._parse_json_response('{"key": "value"}')
            assert result == {"key": "value"}
            
            # Test JSON in markdown code block
            result = node._parse_json_response('```json\n{"key": "value"}\n```')
            assert result == {"key": "value"}
            
            # Test invalid JSON
            result = node._parse_json_response('not json')
            assert result == {}
    
    @patch('src.agents.document_retriever.document_retriever.RAGPipeline')
    def test_no_rag_pipeline_fallback(self, mock_rag, mock_llm, sample_state):
        """Test behavior when RAG pipeline is not available"""
        from src.agents.document_retriever import DocumentRetrieverNode
        
        mock_rag.from_existing_index.side_effect = Exception("Connection failed")
        
        node = DocumentRetrieverNode(llm_model=mock_llm)
        
        result_state = node(sample_state)
        
        # Should handle gracefully
        assert result_state["retrieved_documents"] == []
        assert result_state["current_step"] == 1


class TestDocumentRetrieverPrompts:
    """Test cases for document retriever prompts"""
    
    def test_build_document_retrieval_prompt(self):
        """Test prompt building function"""
        from src.agents.document_retriever.prompts import build_document_retrieval_prompt
        
        prompt = build_document_retrieval_prompt(
            query="Test query",
            context="Test context",
            goal="Test goal",
            symptoms="Test symptoms",
            diagnosis="Test diagnosis",
            retrieved_docs="Test docs"
        )
        
        assert "Test query" in prompt
        assert "Test context" in prompt
        assert "Test goal" in prompt
        assert "Test symptoms" in prompt
        assert "Test diagnosis" in prompt
        assert "Test docs" in prompt
    
    def test_system_prompt_exists(self):
        """Test that system prompt is defined"""
        from src.agents.document_retriever.prompts import DOCUMENT_RETRIEVER_SYSTEM_PROMPT
        
        assert DOCUMENT_RETRIEVER_SYSTEM_PROMPT is not None
        assert len(DOCUMENT_RETRIEVER_SYSTEM_PROMPT) > 0


class TestDocumentRetrieverConfig:
    """Test cases for document retriever configuration"""
    
    @patch('src.agents.document_retriever.config.ChatGoogleGenerativeAI')
    @patch('src.agents.document_retriever.config.GOOGLE_API_KEY', 'test-key')
    def test_get_model_singleton(self, mock_chat):
        """Test that model is created as singleton"""
        from src.agents.document_retriever.config import (
            get_document_retriever_model,
            DocumentRetrieverModelSingleton
        )
        
        # Reset singleton
        DocumentRetrieverModelSingleton.reset()
        
        mock_chat.return_value = Mock()
        
        model1 = get_document_retriever_model()
        model2 = get_document_retriever_model()
        
        # Should be same instance
        assert model1 is model2
        
        # Should only create once
        assert mock_chat.call_count == 1
        
        # Clean up
        DocumentRetrieverModelSingleton.reset()


class TestFactoryFunction:
    """Test factory function"""
    
    @patch('src.agents.document_retriever.document_retriever.RAGPipeline')
    @patch('src.agents.document_retriever.document_retriever.get_document_retriever_model')
    def test_new_document_retriever_node(self, mock_get_model, mock_rag):
        """Test factory function creates node correctly"""
        from src.agents.document_retriever import new_document_retriever_node
        
        mock_get_model.return_value = Mock()
        mock_rag.from_existing_index.return_value = Mock()
        
        node = new_document_retriever_node()
        
        assert node is not None
        assert hasattr(node, '__call__')
    
    @patch('src.agents.document_retriever.document_retriever.RAGPipeline')
    def test_new_document_retriever_node_with_custom_llm(self, mock_rag):
        """Test factory function with custom LLM"""
        from src.agents.document_retriever import new_document_retriever_node
        
        mock_rag.from_existing_index.return_value = Mock()
        custom_llm = Mock()
        
        node = new_document_retriever_node(llm_model=custom_llm)
        
        assert node.llm is custom_llm
