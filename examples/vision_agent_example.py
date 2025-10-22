"""
Example usage of the Gemini Vision Analyzer for medical image analysis.

This demonstrates how to use the GeminiVisionAnalyzer with Gemini 2.0 Flash Lite
for analyzing medical images, performing visual Q&A, and specialized analyses.
"""

import os
import base64
from src.vision.gemini_vision_analyzer import GeminiVisionAnalyzer


def load_image_as_base64(image_path: str) -> str:
    """Load an image file and convert to base64."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    return image_data


def example_basic_analysis():
    """Example: Basic medical image analysis."""
    print("=" * 60)
    print("Example 1: Basic Medical Image Analysis")
    print("=" * 60)
    
    # Initialize analyzer
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return
    
    analyzer = GeminiVisionAnalyzer(api_key)
    
    # Example with a sample image (you would replace with actual image)
    # For demo purposes, using a placeholder
    print("\n[Note: Replace with actual medical image path]")
    
    # Simulate base64 image data (in real usage, load actual image)
    # image_data = load_image_as_base64("path/to/medical/image.jpg")
    
    symptoms = "Tôi có vết đỏ trên da, hơi sưng và ngứa"
    
    print(f"\nSymptoms: {symptoms}")
    print("\nAnalyzing image with Gemini 2.0 Flash Lite...")
    
    # Uncomment when you have actual image:
    # result = analyzer.analyze_image(image_data, symptoms)
    # 
    # print("\n--- Visual Description ---")
    # print(result["visual_description"])
    # 
    # print("\n--- Visual Q&A Results ---")
    # for question, answer in result["visual_qa_results"].items():
    #     print(f"Q: {question}")
    #     print(f"A: {answer}\n")
    # 
    # print(f"Confidence Score: {result['confidence']:.2f}")


def example_skin_analysis():
    """Example: Specialized skin condition analysis."""
    print("\n" + "=" * 60)
    print("Example 2: Skin Condition Analysis")
    print("=" * 60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return
    
    analyzer = GeminiVisionAnalyzer(api_key)
    
    print("\n[Note: Replace with actual skin condition image path]")
    
    # Uncomment when you have actual image:
    # image_data = load_image_as_base64("path/to/skin/image.jpg")
    # result = analyzer.analyze_skin_condition(image_data, "phát ban")
    # 
    # print("\n--- Skin Analysis ---")
    # print(result["analysis"])
    # print(f"\nConfidence: {result['confidence']:.2f}")


def example_wound_analysis():
    """Example: Specialized wound assessment."""
    print("\n" + "=" * 60)
    print("Example 3: Wound Assessment")
    print("=" * 60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return
    
    analyzer = GeminiVisionAnalyzer(api_key)
    
    print("\n[Note: Replace with actual wound image path]")
    
    # Uncomment when you have actual image:
    # image_data = load_image_as_base64("path/to/wound/image.jpg")
    # result = analyzer.analyze_wound(image_data)
    # 
    # print("\n--- Wound Assessment ---")
    # print(result["analysis"])
    # print(f"\nConfidence: {result['confidence']:.2f}")


def example_multi_agent_workflow():
    """Example: Using vision agent in multi-agent workflow."""
    print("\n" + "=" * 60)
    print("Example 4: Multi-Agent Medical Analysis Workflow")
    print("=" * 60)
    
    from src.agents.medical_agent_graph import MedicalAgentGraph
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return
    
    # Initialize multi-agent system
    agent_graph = MedicalAgentGraph(
        google_api_key=api_key
    )
    
    print("\n[Note: Replace with actual medical image path]")
    
    # Uncomment when you have actual image:
    # image_data = load_image_as_base64("path/to/medical/image.jpg")
    # symptoms = "Tôi bị đau và sưng ở vùng này khoảng 2 ngày"
    # 
    # print(f"\nSymptoms: {symptoms}")
    # print("\nRunning multi-agent analysis...")
    # print("Agents: Vision → Symptom Matcher → Risk Assessor → Recommender\n")
    # 
    # result = agent_graph.analyze(image_data, symptoms)
    # 
    # print("\n--- Complete Analysis ---")
    # print("\n1. Visual Analysis:")
    # print(result["visual_analysis"]["visual_description"])
    # 
    # print("\n2. Medical Assessment:")
    # print(result["medical_assessment"])
    # 
    # print(f"\n3. Risk Level: {result['risk_level']}")
    # 
    # print("\n4. Recommendations:")
    # for i, rec in enumerate(result["recommendations"], 1):
    #     print(f"   {i}. {rec}")
    # 
    # print(f"\n5. Confidence: {result['confidence_score']:.2f}")
    # 
    # print("\n--- Workflow Log ---")
    # for msg in result["workflow_messages"]:
    #     print(f"   {msg}")


if __name__ == "__main__":
    print("\n🏥 Gemini Vision Analyzer - Medical Image Analysis Examples")
    print("=" * 60)
    print("\nThese examples show how to use Gemini 2.0 Flash Lite for vision tasks")
    print("in a medical clinic chatbot context.\n")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not found in environment")
        print("Please set it before running the examples:")
        print('export GOOGLE_API_KEY="your-api-key-here"\n')
    
    # Run examples
    example_basic_analysis()
    example_skin_analysis()
    example_wound_analysis()
    example_multi_agent_workflow()
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)
    print("\nTo use with real images:")
    print("1. Uncomment the code blocks in each example")
    print("2. Replace image paths with actual medical images")
    print("3. Make sure GOOGLE_API_KEY is set in your .env file")
    print("4. Run: python examples/vision_agent_example.py\n")
