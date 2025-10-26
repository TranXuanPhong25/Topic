"""
Example usage of the Medical Diagnostic Graph system

This script demonstrates all 4 main flows:
1. Normal Conversation (FAQ)
2. Appointment Booking
3. Symptoms Only Analysis
4. Image + Symptoms Analysis
"""
import os
import sys
from dotenv import load_dotenv
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.medical_diagnostic_graph import MedicalDiagnosticGraph

load_dotenv()


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict):
    """Print analysis result in a formatted way"""
    print(f"✅ Success: {result['success']}")
   #  print(f"🎯 Intent: {result['intent']}")
    print(f"\n📝 Final Response:")
    print("-" * 80)
    print(result['final_response'])
    print("-" * 80)
    
    if result.get('diagnosis'):
        print(f"\n🩺 Diagnosis:")
        print(f"  - Primary: {result['diagnosis'].get('primary_diagnosis', 'N/A')}")
        print(f"  - Severity: {result['diagnosis'].get('severity', 'N/A')}")
    
    if result.get('risk_assessment'):
        print(f"\n⚠️  Risk Level: {result['risk_assessment'].get('risk_level', 'N/A')}")
    
    if result.get('investigation_plan'):
        print(f"\n🔬 Suggested Tests: {len(result['investigation_plan'])} tests")
        for i, test in enumerate(result['investigation_plan'][:3], 1):
            print(f"  {i}. {test.get('test_name', 'N/A')} ({test.get('priority', 'N/A')} priority)")
    
    print(f"\n📋 Execution Log:")
    for message in result.get('messages', []):
        print(f"  {message}")


def example_1_conversation():
    """Example 1: Normal conversation (FAQ)"""
    print_section("Example 1: Normal Conversation - FAQ")
    
    graph = MedicalDiagnosticGraph(google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    questions = [
        "Phòng khám mở cửa lúc mấy giờ?",
        "Có nhận bảo hiểm y tế không?",
        "Địa chỉ phòng khám ở đâu?",
    ]
    
    for question in questions:
        print(f"❓ Question: {question}\n")
        result = graph.analyze(user_input=question)
        print_result(result)
        print("\n")


def example_2_appointment():
    """Example 2: Appointment booking"""
    print_section("Example 2: Appointment Booking")
    
    graph = MedicalDiagnosticGraph(google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Complete appointment request
    print("📅 Scenario A: Complete appointment details\n")
    result = graph.analyze(
        user_input="Tôi muốn đặt lịch khám cho Nguyễn Văn A vào thứ 3 tuần sau lúc 2 giờ chiều để khám tổng quát"
    )
    print_result(result)
    
    print("\n" + "-" * 80 + "\n")
    
    # Incomplete appointment request
    print("📅 Scenario B: Incomplete appointment details\n")
    result = graph.analyze(
        user_input="Tôi muốn đặt lịch khám bệnh"
    )
    print_result(result)


def example_3_symptoms():
    """Example 3: Symptoms only analysis"""
    print_section("Example 3: Symptoms Analysis (No Image)")
    
    graph = MedicalDiagnosticGraph(google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    symptom_cases = [
        {
            "case": "Mild case - Common cold",
            "input": "Tôi bị sổ mũi, hắt hơi và đau họng từ 2 ngày nay"
        },
        {
            "case": "Moderate case - Flu",
            "input": "Tôi bị sốt 38.5 độ C, đau đầu, ho và mệt mỏi từ 3 ngày"
        },
        {
            "case": "Severe case - Respiratory distress",
            "input": "Tôi bị khó thở, đau ngực và ho ra máu"
        }
    ]
    
    for case in symptom_cases:
        print(f"🏥 Case: {case['case']}")
        print(f"💬 Input: {case['input']}\n")
        
        result = graph.analyze(user_input=case['input'])
        print_result(result)
        print("\n" + "-" * 80 + "\n")


def example_4_image_symptoms():
    """Example 4: Image + symptoms analysis"""
    print_section("Example 4: Image + Symptoms Analysis")
    
    graph = MedicalDiagnosticGraph(google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    print("📸 NOTE: This example requires an actual medical image.")
    print("🔧 For testing, you can provide a base64-encoded image.\n")
    
    # Simulated example (in real use, you'd load an actual image)
    print("💬 Input: 'Da tay tôi có vết đỏ này và rất ngứa'\n")
    print("📸 Image: [Base64-encoded image of skin rash]\n")
    
    # Example without actual image (will show how system handles it)
    result = graph.analyze(
        user_input="Da tay tôi có vết đỏ và rất ngứa, có thể là dị ứng",
        image=None  # In real use: image="base64_encoded_string"
    )
    print_result(result)
    
    print("\n💡 To use with actual image:")
    print("""
    import base64
    
    # Load and encode image
    with open('symptom_image.jpg', 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Analyze with image
    result = graph.analyze(
        user_input="Mô tả triệu chứng của bạn",
        image=image_base64
    )
    """)


def example_5_complex_case():
    """Example 5: Complex medical case"""
    print_section("Example 5: Complex Medical Case")
    
    graph = MedicalDiagnosticGraph(google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    complex_case = """
    Tôi là bệnh nhân nữ 45 tuổi. Từ 1 tuần nay, tôi bị:
    - Sốt nhẹ (37.8-38.2°C) vào buổi chiều
    - Đau khớp ở hai bàn tay và cổ tay
    - Mệt mỏi kéo dài
    - Phát ban đỏ ở má
    - Rụng tóc nhiều hơn bình thường
    
    Tôi có tiền sử bệnh lupus trong gia đình (mẹ tôi).
    """
    
    print("🏥 Complex Case: Multiple symptoms with family history")
    print(f"💬 Input:\n{complex_case}\n")
    
    result = graph.analyze(user_input=complex_case)
    print_result(result)


def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║              Medical Diagnostic Graph - Complete Demo                        ║
║                                                                               ║
║  This demo shows all 4 main flows of the LangGraph-based system:            ║
║  1. Normal Conversation (FAQ)                                                ║
║  2. Appointment Booking                                                      ║
║  3. Symptoms Analysis                                                        ║
║  4. Image + Symptoms Analysis                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set your Google API key in .env file:")
        print("  GOOGLE_API_KEY=your-api-key-here")
        return
    
    print("✅ Google API key found. Starting demonstrations...\n")
    
    try:
        # Run examples
        example_1_conversation()
        input("\n⏸️  Press Enter to continue to Example 2...")
        
        example_2_appointment()
        input("\n⏸️  Press Enter to continue to Example 3...")
        
        example_3_symptoms()
        input("\n⏸️  Press Enter to continue to Example 4...")
        
        example_4_image_symptoms()
        input("\n⏸️  Press Enter to continue to Example 5...")
        
        example_5_complex_case()
        
        print_section("Demo Complete!")
        print("""
✅ All examples completed successfully!

📚 For more information:
  - Documentation: docs/LANGGRAPH_IMPLEMENTATION.md
  - Tests: tests/test_medical_diagnostic_graph.py
  - Source: src/agents/medical_diagnostic_graph.py

🚀 Next steps:
  - Integrate with your FastAPI backend
  - Add vector database for better document retrieval
  - Implement knowledge graph for medical context
  - Add real medical image analysis
        """)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
