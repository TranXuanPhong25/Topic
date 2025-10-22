# 🚀 Quick Start Guide - MedGemma Vision Analyzer

## 1-Minute Setup

```bash
# 1. Install dependencies
pip install transformers torch accelerate sentencepiece

# 2. Test it
cd src
python test_medgemma_transformers.py

# 3. Done! ✅
```

## Usage Cheat Sheet

### Basic Usage
```python
from vision.medgemma_vision_analyzer import MedGemmaVisionAnalyzer
import base64

# Initialize
analyzer = MedGemmaVisionAnalyzer()

# Analyze image
result = analyzer.analyze_image(
    image_data="base64_encoded_image",
    symptoms="Patient symptoms here"
)

# Get results
print(result['visual_description'])
print(result['medical_analysis'])
print(result['risk_level'])
print(result['recommendations'])
```

### With ChatBot
```python
from chatbot import ChatBot

bot = ChatBot()
response = await bot.handle_image_message(
    message="Symptoms description",
    image_data=base64_image,
    session_id="user-123"
)
```

### REST API
```bash
curl -X POST http://localhost:8000/chat/image \
  -H "Content-Type: application/json" \
  -d '{"message": "Symptoms", "image": "data:image/png;base64,..."}'
```

## Common Scenarios

### Scenario 1: Skin Rash Analysis
```python
analyzer = MedGemmaVisionAnalyzer()
result = analyzer.analyze_image(
    image_data=rash_image_base64,
    symptoms="Bị phát ban đỏ trên da, hơi ngứa"
)
# Returns: visual description, risk assessment, recommendations
```

### Scenario 2: Wound Assessment
```python
result = analyzer.analyze_image(
    image_data=wound_image_base64,
    symptoms="Vết thương từ tai nạn, không chảy máu"
)
```

### Scenario 3: General Symptoms + Image
```python
result = analyzer.analyze_image(
    image_data=patient_photo_base64,
    symptoms="Sốt 38.5°C, ho, khó thở"
)
```

## Response Format

```python
{
    "visual_description": "Description of what the model sees",
    "medical_analysis": "Medical assessment based on visual + symptoms",
    "risk_level": "low" | "moderate" | "high" | "urgent",
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        ...
    ],
    "confidence": 0.75,  # 0.0 to 1.0
    "image_size": "224x224"
}
```

## Performance Tips

### Speed Up Analysis
```python
# Use GPU if available
analyzer = MedGemmaVisionAnalyzer(device="cuda")

# Or force CPU
analyzer = MedGemmaVisionAnalyzer(device="cpu")
```

### Reduce Memory Usage
```python
# Models are loaded lazily (only when needed)
# First call: slow (loads models)
# Subsequent calls: fast (models cached)
```

### Batch Processing
```python
# Process multiple images
images = [img1_base64, img2_base64, img3_base64]
symptoms_list = ["Symptom 1", "Symptom 2", "Symptom 3"]

results = []
for img, sym in zip(images, symptoms_list):
    result = analyzer.analyze_image(img, sym)
    results.append(result)
```

## Troubleshooting

### Problem: Models not downloading
**Solution**: Check internet connection, try again

### Problem: Out of memory
**Solution**: 
- Close other programs
- Use CPU instead of GPU
- Use smaller models

### Problem: Slow on CPU
**Solution**:
- Use GPU if available
- Wait for first run (model download)
- Reduce image size before encoding

### Problem: Invalid image format
**Solution**: Ensure image is base64 encoded:
```python
import base64
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()
```

## Model Info

| Model | Size | Purpose | Speed (CPU) | Speed (GPU) |
|-------|------|---------|-------------|-------------|
| BLIP | 990MB | Vision | 5-10s | 1-2s |
| Phi-2 | 5.5GB | Medical | 20-40s | 3-5s |

**Total**: ~6.5GB disk space

## Files Created

```
src/vision/
├── __init__.py                          # Module init
├── medgemma_vision_analyzer.py          # Main implementation ⭐
├── README.md                            # Full documentation
└── examples.py                          # Usage examples

src/
├── test_medgemma_transformers.py        # Test script ⭐

Project root/
├── IMPLEMENTATION_SUMMARY.md            # Technical summary
├── COMPLETED.md                         # Achievement summary
└── QUICK_START.md                       # This file ⭐
```

## Next Steps

1. ✅ Test with real medical images
2. ✅ Integrate with frontend (upload button)
3. ✅ Add image preprocessing (resize, normalize)
4. ✅ Implement caching for repeated requests
5. ✅ Add support for multiple image formats
6. ✅ Create image upload UI in frontend

## Support

- **Documentation**: `src/vision/README.md`
- **Examples**: `src/vision/examples.py`
- **Test**: `python src/test_medgemma_transformers.py`

---

**Ready to use!** 🚀

Start with: `python src/test_medgemma_transformers.py`
