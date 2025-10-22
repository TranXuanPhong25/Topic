"""
Unit tests for GeminiVisionAnalyzer

Tests the vision analysis functionality with Gemini 2.0 Flash Lite
"""

import pytest
import base64
import os
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from src.vision.gemini_vision_analyzer import GeminiVisionAnalyzer


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def sample_base64_image():
    """Create a simple test image as base64."""
    # Create a small red square image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


@pytest.fixture
def analyzer(mock_api_key):
    """Create a GeminiVisionAnalyzer instance with mocked API."""
    with patch('src.vision.gemini_vision_analyzer.genai') as mock_genai:
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        analyzer = GeminiVisionAnalyzer(mock_api_key)
        analyzer.model = mock_model
        
        return analyzer


class TestGeminiVisionAnalyzer:
    """Test suite for GeminiVisionAnalyzer."""
    
    def test_initialization(self, mock_api_key):
        """Test that analyzer initializes correctly."""
        with patch('src.vision.gemini_vision_analyzer.genai') as mock_genai:
            analyzer = GeminiVisionAnalyzer(mock_api_key)
            
            # Check that genai.configure was called
            mock_genai.configure.assert_called_once_with(api_key=mock_api_key)
            
            # Check that model was initialized
            mock_genai.GenerativeModel.assert_called_once()
            assert analyzer.google_api_key == mock_api_key
    
    def test_decode_base64_image(self, analyzer, sample_base64_image):
        """Test base64 image decoding."""
        image = analyzer._decode_base64_image(sample_base64_image)
        
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_decode_base64_image_with_data_url(self, analyzer, sample_base64_image):
        """Test decoding image with data URL prefix."""
        data_url = f"data:image/png;base64,{sample_base64_image}"
        image = analyzer._decode_base64_image(data_url)
        
        assert isinstance(image, Image.Image)
        assert image.size == (100, 100)
    
    def test_decode_invalid_base64(self, analyzer):
        """Test error handling for invalid base64."""
        with pytest.raises(ValueError):
            analyzer._decode_base64_image("invalid_base64_string")
    
    def test_calculate_confidence_high(self, analyzer):
        """Test confidence calculation with good data."""
        description = "This is a detailed medical description of the image. " * 5
        qa_results = {
            "Question 1": "Answer 1",
            "Question 2": "Answer 2",
            "Question 3": "Answer 3"
        }
        
        confidence = analyzer._calculate_confidence(description, qa_results)
        
        assert 0.8 <= confidence <= 1.0
    
    def test_calculate_confidence_low(self, analyzer):
        """Test confidence calculation with poor data."""
        description = "Short"
        qa_results = {
            "Q1": "Không thể trả lời",
            "Q2": "Lỗi"
        }
        
        confidence = analyzer._calculate_confidence(description, qa_results)
        
        assert confidence < 0.5
    
    def test_generate_questions_default(self, analyzer):
        """Test question generation with no specific symptoms."""
        questions = analyzer._generate_questions("")
        
        assert len(questions) > 0
        assert len(questions) <= 5
        assert any("sưng" in q for q in questions)
    
    def test_generate_questions_with_symptoms(self, analyzer):
        """Test question generation with specific symptoms."""
        symptoms = "Tôi bị đau và sưng đỏ"
        questions = analyzer._generate_questions(symptoms)
        
        assert len(questions) > 0
        assert len(questions) <= 5
        # Should include pain-related question
        assert any("đau" in q.lower() for q in questions)
    
    def test_generate_questions_wound(self, analyzer):
        """Test question generation for wound symptoms."""
        symptoms = "Tôi có vết thương bị rách"
        questions = analyzer._generate_questions(symptoms)
        
        assert len(questions) > 0
        # Should include wound-related question (check more flexible)
        assert any("thương" in q.lower() for q in questions)
    
    def test_analyze_image_success(self, analyzer, sample_base64_image):
        """Test successful image analysis."""
        # Mock the model response
        mock_response = Mock()
        mock_response.text = "Đây là mô tả chi tiết về hình ảnh y tế."
        analyzer.model.generate_content.return_value = mock_response
        
        result = analyzer.analyze_image(
            sample_base64_image,
            "Tôi có vết đỏ và sưng"
        )
        
        assert "visual_description" in result
        assert "visual_qa_results" in result
        assert "confidence" in result
        assert "error" in result
        
        assert result["error"] is None
        assert len(result["visual_description"]) > 0
        assert 0 <= result["confidence"] <= 1.0
    
    def test_analyze_image_error_handling(self, analyzer):
        """Test error handling in image analysis."""
        # Mock an error
        analyzer.model.generate_content.side_effect = Exception("API Error")
        
        result = analyzer.analyze_image(
            "invalid_image_data",
            "symptoms"
        )
        
        assert result["error"] is not None
        assert result["confidence"] == 0.0
    
    def test_analyze_skin_condition(self, analyzer, sample_base64_image):
        """Test specialized skin condition analysis."""
        mock_response = Mock()
        mock_response.text = "Phân tích da: Vùng da có màu đỏ, hơi sưng."
        analyzer.model.generate_content.return_value = mock_response
        
        result = analyzer.analyze_skin_condition(
            sample_base64_image,
            "phát ban"
        )
        
        assert "analysis" in result
        assert "type" in result
        assert result["type"] == "skin_condition"
        assert "confidence" in result
        assert result["error"] is None
    
    def test_analyze_wound(self, analyzer, sample_base64_image):
        """Test specialized wound assessment."""
        mock_response = Mock()
        mock_response.text = "Đánh giá vết thương: Vết cắt nhỏ, không nhiễm trùng."
        analyzer.model.generate_content.return_value = mock_response
        
        result = analyzer.analyze_wound(sample_base64_image)
        
        assert "analysis" in result
        assert "type" in result
        assert result["type"] == "wound"
        assert "confidence" in result
        assert result["error"] is None
    
    def test_perform_visual_qa(self, analyzer, sample_base64_image):
        """Test visual Q&A functionality."""
        mock_response = Mock()
        mock_response.text = "Có, vùng da có sưng nhẹ."
        analyzer.model.generate_content.return_value = mock_response
        
        image = analyzer._decode_base64_image(sample_base64_image)
        qa_results = analyzer._perform_visual_qa(
            image,
            "Tôi có vết đỏ và sưng"
        )
        
        assert isinstance(qa_results, dict)
        assert len(qa_results) > 0
        
        # All answers should be strings
        for question, answer in qa_results.items():
            assert isinstance(question, str)
            assert isinstance(answer, str)


class TestIntegration:
    """Integration tests (require actual API key)."""
    
    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY not set"
    )
    def test_real_api_call(self, sample_base64_image):
        """Test with real API (only if key available)."""
        api_key = os.getenv("GOOGLE_API_KEY")
        assert api_key is not None, "API key should be set for this test"
        
        analyzer = GeminiVisionAnalyzer(api_key)
        
        result = analyzer.analyze_image(
            sample_base64_image,
            "Đây là hình ảnh test"
        )
        
        # Should get some response
        assert result["error"] is None or "quota" in str(result["error"]).lower()
        assert "visual_description" in result
