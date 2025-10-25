# Testing the Vision Agent

## Quick Fix Summary

### Problem
The `/ma/chat/image` endpoint was returning `null` or incomplete responses even though the workflow completed successfully.

### Root Causes Fixed

1. **Frontend Issue**: Image data was cleared before being sent to API
   - **Fix**: Save `selectedImageData` to temporary variable before clearing
   - **File**: `frontend/index.html`

2. **Backend Issue**: Endpoint returned generic message instead of formatted analysis
   - **Fix**: Format complete response with visual description, assessment, risk level, and recommendations
   - **File**: `src/main.py`

3. **Endpoint Route**: Frontend was calling `/chat/image` instead of `/ma/chat/image`
   - **Fix**: Updated frontend to use correct multi-agent endpoint
   - **File**: `frontend/index.html`

## Testing

### 1. Start the Server

```bash
cd src
python main.py
```

Server should start on `http://localhost:8000`

### 2. Test with Script

```bash
# From project root
python test_vision_endpoint.py
```

This will:
- Create a test image (red square)
- Send it with symptoms to `/ma/chat/image`
- Display the complete response

### 3. Test in Browser

1. Open `http://localhost:8000` in your browser
2. Click the 📷 camera button in the chat widget
3. Select an image (any medical image or photo)
4. Type symptoms (Vietnamese): "Tôi có vết đỏ trên da, hơi sưng"
5. Click send ➤

### Expected Response

You should see a formatted response like:

```
**Phân tích hình ảnh y tế hoàn tất**

🔍 Mô tả hình ảnh:
[Detailed visual description in Vietnamese]

🩺 Đánh giá y tế:
[Medical assessment combining visual + symptoms]

⚠️ Mức độ khẩn cấp: MEDIUM

💡 Khuyến nghị:
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

**Độ tin cậy:** 85%
```

## What Was Fixed

### Frontend (`frontend/index.html`)

**Before:**
```javascript
const hasImage = selectedImageData !== null;
removeImage(); // ← Cleared data too early!
response = await sendImageToAPI(message, selectedImageData); // ← null!
```

**After:**
```javascript
const imageDataToSend = selectedImageData; // ← Save first
removeImage(); // ← Then clear UI
response = await sendImageToAPI(message, imageDataToSend); // ← Use saved data ✅
```

### Backend (`src/main.py`)

**Before:**
```python
return {
    "response": "Multi-agent analysis completed. See console for details.",
    # ← Not helpful for frontend!
}
```

**After:**
```python
response_text = f"""**Phân tích hình ảnh y tế hoàn tất**

**🔍 Mô tả hình ảnh:**
{result['visual_analysis']['visual_description']}

**🩺 Đánh giá y tế:**
{result['medical_assessment']}
...
"""

return {
    "response": response_text,  # ← Formatted for display ✅
    "analysis": result,         # ← Complete data ✅
}
```

## Architecture Flow

```
User uploads image + symptoms
         ↓
Frontend (index.html)
  - Saves image to imageDataToSend
  - Sends POST to /ma/chat/image
         ↓
Backend (main.py)
  - Validates image
  - Initializes MedicalAgentGraph
  - Runs workflow
         ↓
Multi-Agent Workflow
  1. Vision Agent → Analyzes image (Gemini Vision)
  2. Symptom Matcher → Combines visual + text
  3. Risk Assessor → Determines urgency
  4. Recommender → Provides actions
         ↓
Backend formats response
  - Visual description
  - Medical assessment
  - Risk level
  - Recommendations
  - Confidence score
         ↓
Frontend displays formatted result
```

## Debugging

### Check Server Logs

When you send an image, you should see in the console:

```
============================================================
🏥 Multi-Agent Medical Image Analysis
============================================================
Session: test_session_123
Symptoms: Tôi có vết đỏ trên da...

Running workflow: Vision → Symptom Matcher → Risk Assessor → Recommender

🔍 Vision Agent: Starting image analysis...
✅ Vision Agent: Analysis complete...
🩺 Symptom Matcher: Correlating visual + text symptoms...
✅ Symptom Matcher: Assessment complete
⚠️  Risk Assessor: Determining urgency level...
✅ Risk Assessor: Level = MEDIUM
💡 Recommender: Generating recommendations...
✅ Recommender: Generated 4 recommendations

============================================================
📊 Analysis Results
============================================================
...
```

### Common Issues

**"Cannot connect to server"**
- Make sure server is running: `python src/main.py`
- Check server is on port 8000: `http://localhost:8000/health`

**"GOOGLE_API_KEY not configured"**
- Set API key in `.env` file:
  ```bash
  echo "GOOGLE_API_KEY=your-key-here" > .env
  ```

**Image too large**
- Max size: 10MB (base64 encoded)
- Compress or resize image before uploading

**Workflow takes too long**
- Normal: 10-30 seconds (4 agents running sequentially)
- Check internet connection (calls Gemini API)

## Files Modified

1. ✅ `frontend/index.html` - Fixed image data handling
2. ✅ `src/main.py` - Fixed response formatting  
3. ✅ `test_vision_endpoint.py` - Test script (NEW)
4. ✅ `TESTING_VISION.md` - This file (NEW)

## Next Steps

- Test with real medical images
- Adjust prompts in `src/vision/gemini_vision_analyzer.py`
- Add more error handling
- Implement response caching
- Add image quality validation

## Success Criteria

✅ Image uploads successfully  
✅ Preview shows in chat widget  
✅ API receives base64 image data  
✅ All 4 agents execute in sequence  
✅ Response includes visual description  
✅ Response includes medical assessment  
✅ Response includes risk level (LOW/MEDIUM/HIGH/CRITICAL)  
✅ Response includes 3-5 recommendations  
✅ Confidence score is calculated  
✅ Frontend displays formatted response  

---

**Last Updated**: January 2025  
**Status**: ✅ All fixes implemented and tested
