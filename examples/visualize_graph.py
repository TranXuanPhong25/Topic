"""
Visualize the Medical Diagnostic Graph structure
Creates a text-based visualization of the graph flow
"""

def print_graph_visualization():
    """Print ASCII art visualization of the graph"""
    
    visualization = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MEDICAL DIAGNOSTIC GRAPH - LANGGRAPH                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

                                ┌────────────────┐
                                │                │
                                │     ROUTER     │ ◄── Entry Point
                                │  (Classifier)  │
                                │                │
                                └────────┬───────┘
                                         │
                                         │ Conditional Routing
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         │                               │                               │
    intent:                         intent:                         intent:
 normal_conversation              needs_examiner              symptoms_only/image
         │                               │                               │
         │                               │                               │
         ▼                               ▼                               ▼
┌────────────────────┐          ┌────────────────┐            ┌──────────────────┐
│                    │          │                │            │  ImageAnalyzer   │◄─┐
│ ConversationAgent  │          │  Appointment   │            │   (if image)     │  │
│   (FAQ + Tools)    │          │   Scheduler    │            └────────┬─────────┘  │
│                    │          │                │                     │            │
└─────────┬──────────┘          └────────┬───────┘                     │            │
          │                              │                             │            │
          │                              │                   ┌─────────▼─────────┐  │
          │                              │                   │                   │  │
          ▼                              ▼                   │ CombineAnalysis   │  │
         END                            END                  │ (Merge Symptoms)  │  │
                                                             │                   │  │
                                                             └─────────┬─────────┘  │
                                                                       │            │
                                                                       │            │
                 ┌─────────────────────────────────────────────────────┴────────────┘
                 │                        (symptoms_only path joins here)
                 │
                 ▼
        ┌────────────────────┐
        │                    │
        │  DiagnosisEngine   │
        │  + Risk Assessor   │
        │                    │
        └─────────┬──────────┘
                  │
                  │ Parallel Execution
                  │
      ┌───────────┴──────────┐
      │                      │
      │                      │
      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│                 │   │                 │
│ Investigation   │   │   Document      │
│   Generator     │   │   Retriever     │
│ (Suggest Tests) │   │ (Get Context)   │
│                 │   │                 │
└────────┬────────┘   └────────┬────────┘
         │                     │
         │                     │
         │   ┌─────────────────┘
         │   │
         └───┼─────► Synchronization (Joiner)
             │
             ▼
    ┌────────────────────┐
    │                    │
    │   Recommender      │
    │ (Final Synthesis)  │
    │                    │
    └─────────┬──────────┘
              │
              │
              ▼
             END


═══════════════════════════════════════════════════════════════════════════════
                            NODE DESCRIPTIONS
═══════════════════════════════════════════════════════════════════════════════

1. ROUTER (Entry Point)
   ├─ Input: user_input, image (optional)
   ├─ Action: Classify intent using Gemini
   └─ Output: intent, symptoms

2. CONVERSATION AGENT (Intent: normal_conversation)
   ├─ Input: user_input
   ├─ Action: Search FAQ, generate response
   ├─ Tools: FAQTool, ClinicInfoTool, PriceTableTool
   └─ Output: conversation_output → END

3. APPOINTMENT SCHEDULER (Intent: needs_examiner)
   ├─ Input: user_input
   ├─ Action: Extract appointment details, validate
   └─ Output: appointment_details → END

4. IMAGE ANALYZER (Intent: image_and_symptoms)
   ├─ Input: image, symptoms
   ├─ Action: Analyze image with GeminiVision
   └─ Output: image_analysis_result

5. COMBINE ANALYSIS
   ├─ Input: symptoms, image_analysis_result
   ├─ Action: Merge text + visual findings
   └─ Output: combined_analysis

6. DIAGNOSIS ENGINE (Core Diagnostic)
   ├─ Input: combined_analysis OR symptoms
   ├─ Action: Generate diagnosis + risk assessment
   └─ Output: diagnosis, risk_assessment

7. INVESTIGATION GENERATOR (Parallel Branch 1)
   ├─ Input: diagnosis
   ├─ Action: Suggest medical tests
   └─ Output: investigation_plan

8. DOCUMENT RETRIEVER (Parallel Branch 2)
   ├─ Input: diagnosis
   ├─ Action: Query Vector DB + Knowledge Graph
   └─ Output: retrieved_documents

9. RECOMMENDER (Joiner)
   ├─ Input: investigation_plan, retrieved_documents, diagnosis
   ├─ Action: Synthesize final recommendations
   └─ Output: recommendation, final_response → END


═══════════════════════════════════════════════════════════════════════════════
                           INTENT ROUTING TABLE
═══════════════════════════════════════════════════════════════════════════════

┌────────────────────────┬─────────────────────┬──────────────────────────────┐
│ Intent Type            │ Route               │ Example Input                │
├────────────────────────┼─────────────────────┼──────────────────────────────┤
│ normal_conversation    │ ConversationAgent   │ "Phòng khám mở cửa lúc nào?" │
│                        │        ↓            │ "Có nhận bảo hiểm không?"    │
│                        │       END           │                              │
├────────────────────────┼─────────────────────┼──────────────────────────────┤
│ needs_examiner         │ AppointmentScheduler│ "Tôi muốn đặt lịch"          │
│                        │        ↓            │ "Gặp bác sĩ khi nào?"        │
│                        │       END           │                              │
├────────────────────────┼─────────────────────┼──────────────────────────────┤
│ symptoms_only          │ DiagnosisEngine     │ "Tôi bị sốt và ho"           │
│                        │        ↓            │ "Đau đầu từ 3 ngày"          │
│                        │    [Parallel]       │                              │
│                        │        ↓            │                              │
│                        │   Recommender       │                              │
│                        │        ↓            │                              │
│                        │       END           │                              │
├────────────────────────┼─────────────────────┼──────────────────────────────┤
│ image_and_symptoms     │ ImageAnalyzer       │ "Da tôi có vết đỏ" + [image] │
│                        │        ↓            │                              │
│                        │  CombineAnalysis    │                              │
│                        │        ↓            │                              │
│                        │ DiagnosisEngine     │                              │
│                        │        ↓            │                              │
│                        │    [Parallel]       │                              │
│                        │        ↓            │                              │
│                        │   Recommender       │                              │
│                        │        ↓            │                              │
│                        │       END           │                              │
└────────────────────────┴─────────────────────┴──────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
                            STATE FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

Input: "Tôi bị sốt 38.5°C và ho từ 3 ngày"

1. Router:
   ├─ Classifies: intent = "symptoms_only"
   └─ Extracts: symptoms = "sốt 38.5°C, ho, 3 ngày"

2. DiagnosisEngine:
   ├─ Analyzes symptoms
   ├─ Diagnosis: "Cúm mùa (có thể)"
   ├─ Severity: "moderate"
   └─ Risk: "MEDIUM"

3. Parallel Execution:
   ├─ InvestigationGenerator:
   │  ├─ "Xét nghiệm máu tổng quát" (high priority)
   │  └─ "X-quang phổi" (medium priority)
   │
   └─ DocumentRetriever:
      ├─ FAQ: "Cúm mùa thường kéo dài 7-10 ngày"
      └─ Knowledge: "Thông tin y khoa về cúm"

4. Recommender (Joiner):
   ├─ Combines all information
   └─ Final Response:
      "🩺 Phân tích y tế:
       Chẩn đoán: Cúm mùa
       Rủi ro: MEDIUM
       
       💡 Khuyến nghị:
       1. Nghỉ ngơi, uống nhiều nước
       2. Gặp bác sĩ nếu sốt > 39°C
       3. Xét nghiệm máu nếu không giảm
       ..."

5. → END


═══════════════════════════════════════════════════════════════════════════════
                         GRAPH EXECUTION METRICS
═══════════════════════════════════════════════════════════════════════════════

Conversation Flow:        Router → ConversationAgent → END          (~2s)
Appointment Flow:         Router → AppointmentScheduler → END       (~2s)
Symptoms Only Flow:       Router → Diagnosis → [Parallel] → Rec.   (~10s)
Image + Symptoms Flow:    Router → Image → Combine → Diag → Rec.   (~15s)

Parallel Execution:       Investigation + Retrieval (simultaneous)
Synchronization Point:    Recommender waits for both branches
Total Nodes:              9 nodes
End Points:               3 (Conversation, Appointment, Recommender)


═══════════════════════════════════════════════════════════════════════════════
                          IMPLEMENTATION FILES
═══════════════════════════════════════════════════════════════════════════════

Core:       src/agents/medical_diagnostic_graph.py
Tests:      tests/test_medical_diagnostic_graph.py
Demo:       examples/medical_diagnostic_graph_demo.py
Docs:       docs/LANGGRAPH_IMPLEMENTATION.md
            docs/DIAGNOSTIC_GRAPH_QUICKSTART.md
            docs/IMPLEMENTATION_SUMMARY.md

"""
    
    print(visualization)


def print_state_structure():
    """Print the GraphState structure"""
    
    print("\n" + "="*80)
    print("                         GRAPH STATE STRUCTURE")
    print("="*80 + "\n")
    
    state_fields = [
        ("input", "str", "Initial user query"),
        ("intent", "str", "Classified intent (4 types)"),
        ("image", "Optional[str]", "Base64 encoded image"),
        ("symptoms", "str", "Extracted symptoms from input"),
        ("image_analysis_result", "Dict[str, Any]", "Vision analysis output"),
        ("combined_analysis", "str", "Merged symptoms + image"),
        ("diagnosis", "Dict[str, Any]", "Diagnostic results"),
        ("risk_assessment", "Dict[str, Any]", "Risk evaluation"),
        ("investigation_plan", "List[Dict]", "Suggested medical tests"),
        ("retrieved_documents", "List[Dict]", "Retrieved context"),
        ("recommendation", "str", "Final actionable advice"),
        ("conversation_output", "str", "Conversational response"),
        ("appointment_details", "Dict[str, Any]", "Booking information"),
        ("final_response", "str", "User-facing message"),
        ("messages", "List[str]", "Execution log"),
        ("metadata", "Dict[str, Any]", "Additional context"),
    ]
    
    print(f"{'Field':<25} {'Type':<25} {'Description':<30}")
    print("-" * 80)
    for field, field_type, description in state_fields:
        print(f"{field:<25} {field_type:<25} {description:<30}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print_graph_visualization()
    print_state_structure()
    
    print("\n" + "="*80)
    print("For detailed documentation, see:")
    print("  • docs/LANGGRAPH_IMPLEMENTATION.md")
    print("  • docs/DIAGNOSTIC_GRAPH_QUICKSTART.md")
    print("  • docs/IMPLEMENTATION_SUMMARY.md")
    print("="*80 + "\n")
