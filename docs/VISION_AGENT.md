# Gemini Vision Agent for Medical Image Analysis

This module implements a vision analysis agent using **Google Gemini 2.0 Flash Lite** for medical image analysis tasks. It provides intelligent image understanding capabilities for medical clinic chatbots.

## Features

### 🎯 Core Capabilities
- **Visual Description Generation**: Detailed, medical-focused image descriptions
- **Visual Question Answering**: Context-aware Q&A based on patient symptoms
- **Skin Condition Analysis**: Specialized dermatology assessments
- **Wound Assessment**: Detailed wound evaluation and infection detection
- **Confidence Scoring**: Automatic quality assessment of analysis results

### 🤖 Multi-Agent Integration
The vision agent integrates seamlessly with the LangGraph multi-agent workflow:
1. **Vision Agent** → Analyzes medical images
2. **Symptom Matcher** → Correlates visual findings with text symptoms
3. **Risk Assessor** → Determines urgency level
4. **Recommender** → Provides actionable next steps

## Technology

### Why Gemini 2.0 Flash Lite?
- ✅ **Multimodal**: Native support for image + text input
- ✅ **Fast**: Optimized for quick responses
- ✅ **Free Tier**: Generous free quota for learning projects
- ✅ **High Quality**: State-of-the-art vision understanding
- ✅ **Simple API**: Easy to integrate and use

### Model Configuration
```python
model_name = "gemini-2.0-flash-lite"
temperature = 0.4  # Balanced creativity and consistency
max_output_tokens = 2048
```

## Installation

### Dependencies
```bash
pip install google-generativeai Pillow
```

### API Key Setup
```bash
# Add to .env file
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Basic Image Analysis
```python
from src.vision.gemini_vision_analyzer import GeminiVisionAnalyzer

# Initialize
analyzer = GeminiVisionAnalyzer(google_api_key="your-key")

# Analyze image with symptoms
result = analyzer.analyze_image(
    image_data=base64_image,
    symptoms_text="Tôi có vết đỏ trên da, hơi sưng và ngứa"
)

# Access results
print(result["visual_description"])
print(result["visual_qa_results"])
print(f"Confidence: {result['confidence']}")
```

### Specialized Analyses

#### Skin Condition Analysis
```python
result = analyzer.analyze_skin_condition(
    image_data=base64_image,
    specific_concern="phát ban"  # rash
)

print(result["analysis"])
# Output: Detailed dermatological assessment
```

#### Wound Assessment
```python
result = analyzer.analyze_wound(image_data=base64_image)

print(result["analysis"])
# Output: Wound type, size, infection signs, care recommendations
```

### Multi-Agent Workflow
```python
from src.agents.medical_agent_graph import MedicalAgentGraph

# Initialize multi-agent system
agent_graph = MedicalAgentGraph(google_api_key="your-key")

# Run complete analysis
result = agent_graph.analyze(
    image_data=base64_image,
    symptoms_text="Tôi bị đau và sưng ở vùng này khoảng 2 ngày"
)

# Access comprehensive results
print(result["visual_analysis"])      # Vision agent output
print(result["medical_assessment"])    # Symptom matcher output
print(result["risk_level"])            # Risk assessor output
print(result["recommendations"])       # Recommender output
print(result["workflow_messages"])     # Complete workflow log
```

## Architecture

### GeminiVisionAnalyzer Class

#### Methods
- `analyze_image(image_data, symptoms_text)` - General medical image analysis
- `analyze_skin_condition(image_data, specific_concern)` - Dermatology focus
- `analyze_wound(image_data)` - Wound care focus

#### Internal Methods
- `_decode_base64_image()` - Convert base64 to PIL Image
- `_generate_visual_description()` - Create detailed image description
- `_perform_visual_qa()` - Answer symptom-specific questions
- `_generate_questions()` - Generate relevant questions based on symptoms
- `_calculate_confidence()` - Score analysis quality

### Data Flow
```
Base64 Image → PIL Image → Gemini Vision API → Analysis Results
     ↓
Symptoms Text → Question Generation → Visual Q&A → Q&A Results
     ↓
Combined Analysis → Confidence Score → Return to User
```

## Example Output

### Visual Description
```
"Hình ảnh cho thấy một vùng da ở cánh tay với vết đỏ kích thước khoảng 3-4cm. 
Vùng này có màu đỏ hồng, hơi sưng nổi so với da xung quanh. Bề mặt da trông khô, 
không thấy dấu hiệu tiết dịch hoặc vảy rõ rệt. Ranh giới của vùng đỏ tương đối 
rõ ràng. Không quan sát thấy vết thương hở hoặc dấu hiệu nhiễm trùng nghiêm trọng."
```

### Visual Q&A Results
```python
{
    "Có thấy dấu hiệu sưng tấy không?": 
        "Có, vùng da có sưng nhẹ, nổi cao hơn da xung quanh khoảng 2-3mm.",
    
    "Màu sắc có bất thường không?": 
        "Có màu đỏ hồng bất thường, khác với màu da bình thường xung quanh.",
    
    "Có thấy dấu hiệu nhiễm trùng không?": 
        "Không thấy dấu hiệu nhiễm trùng rõ rệt như mủ hoặc tiết dịch."
}
```

### Confidence Score
- `0.8-1.0`: High confidence, detailed analysis
- `0.5-0.8`: Medium confidence, reasonable analysis
- `0.0-0.5`: Low confidence, limited information

## Best Practices

### Image Quality
- ✅ Clear, well-lit photos
- ✅ Close-up of affected area
- ✅ In focus, not blurry
- ✅ Good contrast
- ❌ Too dark or overexposed
- ❌ Too far away
- ❌ Obstructed view

### Symptom Descriptions
Provide context for better Q&A:
- Duration: "3 ngày nay"
- Symptoms: "đau, sưng, ngứa"
- Changes: "ngày càng tệ hơn"
- Other: "sau khi bị cào"

### Error Handling
```python
result = analyzer.analyze_image(image_data, symptoms)

if result["error"]:
    print(f"Analysis failed: {result['error']}")
else:
    # Process successful result
    pass
```

## Testing

Run the example file:
```bash
python examples/vision_agent_example.py
```

Run unit tests:
```bash
pytest tests/test_vision_analyzer.py -v
```

## Limitations

### Educational Project Notice
⚠️ **This is an educational project for learning chatbot development.**

For production medical use, add:
- HIPAA compliance
- Security audits
- Professional medical review
- Regulatory approvals
- Liability insurance

### Medical Disclaimers
- ❌ Not a substitute for professional medical advice
- ❌ Not for emergency situations (call 911)
- ❌ Analysis is descriptive, not diagnostic
- ✅ Helps with appointment scheduling
- ✅ Provides general information
- ✅ Assists with triage

## Advanced Features

### Custom Prompts
Modify prompts in `GeminiVisionAnalyzer` for:
- Different languages
- Specific medical specialties
- Custom question sets
- Different output formats

### Integration Points
- **FastAPI endpoints**: Add vision analysis to chat API
- **Database storage**: Save analysis results
- **Todo system**: Create follow-up tasks based on findings
- **Appointment scheduling**: Auto-schedule based on risk level

## Troubleshooting

### Common Issues

**API Key Error**
```
Error: GOOGLE_API_KEY not found
Solution: Set environment variable or add to .env
```

**Image Decode Error**
```
Error: Invalid image data
Solution: Ensure base64 string is properly formatted
```

**Low Confidence Score**
```
Confidence < 0.5
Solution: Check image quality, provide more symptom context
```

## Contributing

### Adding New Analysis Types
1. Create new method in `GeminiVisionAnalyzer`
2. Design specialized prompt
3. Add to examples
4. Write tests

### Improving Prompts
- Test with various images
- Collect feedback
- Iterate on Vietnamese phrasing
- Add medical terminology

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Project Quick Start](../QUICK_START.md)
- [Main README](../README.md)

## License

Educational use only. See project LICENSE for details.

## Contact

For questions about vision agent implementation:
- Check examples in `examples/vision_agent_example.py`
- Review code in `src/vision/gemini_vision_analyzer.py`
- See multi-agent workflow in `src/agents/medical_agent_graph.py`
