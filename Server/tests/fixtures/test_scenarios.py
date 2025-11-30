"""
Test Dataset: Medical Diagnostic Scenarios
Diverse test cases for evaluating agentic capabilities
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TestScenario:
    """Test scenario with input, expectations, and metadata"""
    id: str
    name: str
    description: str
    category: str
    
    # Input
    input_text: str
    image: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None
    
    # Expected behavior
    expected_agents: Optional[List[str]] = None
    expected_plan_length: Optional[int] = None
    expected_severity: Optional[str] = None
    expected_red_flags: Optional[List[str]] = None
    
    # Constraints
    expected_language: str = "English"
    expected_style: Optional[str] = None
    urgency_level: str = "Routine"
    
    # Performance expectations
    max_latency_seconds: float = 15.0
    
    # Ground truth (for accuracy evaluation)
    ground_truth_diagnosis: Optional[str] = None
    ground_truth_conditions: Optional[List[str]] = None


# ============================================================================
# 1. SIMPLE DIAGNOSIS SCENARIOS
# ============================================================================

SIMPLE_DIAGNOSIS_SCENARIOS = [
    TestScenario(
        id="simple_001",
        name="Simple Fever and Headache",
        description="Basic symptom reporting - fever and headache",
        category="simple_diagnosis",
        input_text="I have fever and headache for 2 days",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="LOW",
        max_latency_seconds=10.0,
        ground_truth_conditions=["viral infection", "flu", "common cold"]
    ),
    
    TestScenario(
        id="simple_002",
        name="Cough and Sore Throat",
        description="Respiratory symptoms - cough and sore throat",
        category="simple_diagnosis",
        input_text="I have a cough and sore throat that started 3 days ago",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="LOW",
        max_latency_seconds=10.0,
        ground_truth_conditions=["pharyngitis", "viral upper respiratory infection"]
    ),
    
    TestScenario(
        id="simple_003",
        name="Nausea and Vomiting",
        description="Gastrointestinal symptoms",
        category="simple_diagnosis",
        input_text="Feeling nauseous with vomiting since yesterday",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="MODERATE",
        max_latency_seconds=10.0,
        ground_truth_conditions=["gastroenteritis", "food poisoning"]
    ),
]


# ============================================================================
# 2. EMERGENCY SCENARIOS
# ============================================================================

EMERGENCY_SCENARIOS = [
    TestScenario(
        id="emergency_001",
        name="Chest Pain Cardiac Emergency",
        description="Critical cardiac symptoms requiring immediate attention",
        category="emergency",
        input_text="Severe chest pain radiating to left arm, difficulty breathing, cold sweats",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="EMERGENCY",
        expected_red_flags=["chest pain", "breathing difficulty", "radiation to arm"],
        urgency_level="Emergency",
        max_latency_seconds=5.0,
        ground_truth_diagnosis="Possible myocardial infarction (heart attack) - CALL 911"
    ),
    
    TestScenario(
        id="emergency_002",
        name="Severe Headache with Neurological Signs",
        description="Potential stroke or meningitis",
        category="emergency",
        input_text="Sudden severe headache, confusion, stiff neck, sensitivity to light",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="EMERGENCY",
        expected_red_flags=["sudden severe headache", "confusion", "stiff neck"],
        urgency_level="Emergency",
        max_latency_seconds=5.0,
        ground_truth_conditions=["meningitis", "subarachnoid hemorrhage", "stroke"]
    ),
    
    TestScenario(
        id="emergency_003",
        name="Difficulty Breathing",
        description="Respiratory distress",
        category="emergency",
        input_text="Can't breathe properly, wheezing, chest tightness",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="EMERGENCY",
        expected_red_flags=["breathing difficulty", "wheezing"],
        urgency_level="Emergency",
        max_latency_seconds=5.0,
        ground_truth_conditions=["asthma exacerbation", "anaphylaxis", "pulmonary embolism"]
    ),
]


# ============================================================================
# 3. VIETNAMESE LANGUAGE SCENARIOS
# ============================================================================

VIETNAMESE_SCENARIOS = [
    TestScenario(
        id="vietnamese_001",
        name="Vietnamese Fever Symptoms",
        description="Test Vietnamese language constraint adherence",
        category="language_constraint",
        input_text="Tôi bị sốt và đau đầu 2 ngày rồi",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="LOW",
        expected_language="Vietnamese",
        max_latency_seconds=10.0,
        ground_truth_conditions=["nhiễm virus", "cảm cúm"]
    ),
    
    TestScenario(
        id="vietnamese_002",
        name="Vietnamese Treatment Request",
        description="User requests treatment advice in Vietnamese",
        category="language_constraint",
        input_text="Tôi nên làm gì để điều trị bệnh này?",
        chat_history=[
            {"role": "user", "content": "Tôi bị đau bụng"},
            {"role": "assistant", "content": "Có thể là viêm dạ dày..."}
        ],
        expected_agents=["recommender", "synthesis"],
        expected_language="Vietnamese",
        expected_style="Detailed",
        max_latency_seconds=15.0
    ),
    
    TestScenario(
        id="vietnamese_003",
        name="Vietnamese Emergency",
        description="Emergency case in Vietnamese",
        category="emergency",
        input_text="Đau ngực dữ dội, lan ra cánh tay trái, ra mồ hôi lạnh",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_severity="EMERGENCY",
        expected_language="Vietnamese",
        urgency_level="Emergency",
        max_latency_seconds=5.0,
        ground_truth_diagnosis="Cơn đau tim có thể xảy ra - GỌI CẤP CỨU NGAY"
    ),
]


# ============================================================================
# 4. MULTI-TURN CONVERSATION SCENARIOS
# ============================================================================

MULTI_TURN_SCENARIOS = [
    TestScenario(
        id="multi_turn_001",
        name="Progressive Symptom Disclosure",
        description="User reveals symptoms across multiple turns",
        category="multi_turn",
        input_text="Now the pain is worse and I have nausea",
        chat_history=[
            {"role": "user", "content": "I have a headache"},
            {"role": "assistant", "content": "How long have you had this headache?"},
            {"role": "user", "content": "Since yesterday morning"}
        ],
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        expected_severity="MODERATE",
        max_latency_seconds=12.0
    ),
    
    TestScenario(
        id="multi_turn_002",
        name="Follow-up with Additional Details",
        description="User provides additional info when asked",
        category="multi_turn",
        input_text="Yes, and I also feel dizzy when standing up",
        chat_history=[
            {"role": "assistant", "content": "Do you have any other symptoms besides the fever?"},
            {"role": "user", "content": "I'm very tired"}
        ],
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        max_latency_seconds=12.0
    ),
]


# ============================================================================
# 5. MIXED INTENT SCENARIOS
# ============================================================================

MIXED_INTENT_SCENARIOS = [
    TestScenario(
        id="mixed_001",
        name="Symptoms with FAQ",
        description="User asks medical question and clinic info together",
        category="mixed_intent",
        input_text="Hello! I have fever and cough. Also, what are your clinic hours?",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_plan_length=2,
        max_latency_seconds=12.0
    ),
    
    TestScenario(
        id="mixed_002",
        name="Diagnosis Request with Appointment",
        description="User wants diagnosis and to book appointment",
        category="mixed_intent",
        input_text="I have chest pain. Can I get an appointment today?",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        expected_severity="MODERATE",
        max_latency_seconds=15.0
    ),
]


# ============================================================================
# 6. FAQ AND CONVERSATION SCENARIOS
# ============================================================================

FAQ_SCENARIOS = [
    TestScenario(
        id="faq_001",
        name="Clinic Hours Question",
        description="Simple FAQ about clinic hours",
        category="faq",
        input_text="What are your clinic hours?",
        expected_agents=["conversation_agent"],
        expected_plan_length=1,
        max_latency_seconds=5.0
    ),
    
    TestScenario(
        id="faq_002",
        name="General Medical Question",
        description="General health information request",
        category="faq",
        input_text="What is diabetes?",
        expected_agents=["conversation_agent"],
        expected_plan_length=1,
        max_latency_seconds=8.0
    ),
]


# ============================================================================
# 7. APPOINTMENT SCENARIOS
# ============================================================================

APPOINTMENT_SCENARIOS = [
    TestScenario(
        id="appointment_001",
        name="Simple Appointment Booking",
        description="Direct appointment request",
        category="appointment",
        input_text="I want to book an appointment for next Tuesday",
        expected_agents=["appointment_scheduler"],
        expected_plan_length=1,
        max_latency_seconds=8.0
    ),
    
    TestScenario(
        id="appointment_002",
        name="Appointment with Specific Doctor",
        description="Request for specific provider",
        category="appointment",
        input_text="Can I see Dr. Smith next week for a checkup?",
        expected_agents=["appointment_scheduler"],
        expected_plan_length=1,
        max_latency_seconds=8.0
    ),
]


# ============================================================================
# 8. EDGE CASES AND ERROR SCENARIOS
# ============================================================================

EDGE_CASE_SCENARIOS = [
    TestScenario(
        id="edge_001",
        name="Vague Symptoms",
        description="User provides very vague symptom description",
        category="edge_case",
        input_text="I don't feel well",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        # Should ask for more information
        max_latency_seconds=10.0
    ),
    
    TestScenario(
        id="edge_002",
        name="Multiple Unrelated Symptoms",
        description="User lists many disparate symptoms",
        category="edge_case",
        input_text="I have headache, foot pain, rash, and insomnia for weeks",
        expected_agents=["symptom_extractor", "diagnosis_engine"],
        max_latency_seconds=15.0
    ),
    
    TestScenario(
        id="edge_003",
        name="Empty Input",
        description="User sends empty or whitespace-only input",
        category="edge_case",
        input_text="   ",
        expected_agents=["conversation_agent"],
        max_latency_seconds=5.0
    ),
]


# ============================================================================
# DATASET COLLECTIONS
# ============================================================================

ALL_SCENARIOS = (
    SIMPLE_DIAGNOSIS_SCENARIOS +
    EMERGENCY_SCENARIOS +
    VIETNAMESE_SCENARIOS +
    MULTI_TURN_SCENARIOS +
    MIXED_INTENT_SCENARIOS +
    FAQ_SCENARIOS +
    APPOINTMENT_SCENARIOS +
    EDGE_CASE_SCENARIOS
)


def get_scenarios_by_category(category: str) -> List[TestScenario]:
    """Get all scenarios for a specific category"""
    return [s for s in ALL_SCENARIOS if s.category == category]


def get_scenario_by_id(scenario_id: str) -> Optional[TestScenario]:
    """Get a specific scenario by ID"""
    for scenario in ALL_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    return None


# Summary statistics
def print_dataset_summary():
    """Print summary of test dataset"""
    print("\n" + "="*70)
    print("📋 TEST DATASET SUMMARY")
    print("="*70)
    
    categories = {}
    for scenario in ALL_SCENARIOS:
        categories[scenario.category] = categories.get(scenario.category, 0) + 1
    
    print(f"\nTotal Scenarios: {len(ALL_SCENARIOS)}")
    print("\nBy Category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    
    emergency_count = sum(1 for s in ALL_SCENARIOS if s.urgency_level == "Emergency")
    vietnamese_count = sum(1 for s in ALL_SCENARIOS if s.expected_language == "Vietnamese")
    
    print(f"\nSpecial Cases:")
    print(f"  Emergency scenarios: {emergency_count}")
    print(f"  Vietnamese language: {vietnamese_count}")
    print(f"  Multi-turn: {len(MULTI_TURN_SCENARIOS)}")
    print(f"  With ground truth: {sum(1 for s in ALL_SCENARIOS if s.ground_truth_diagnosis or s.ground_truth_conditions)}")
    
    print("="*70)


if __name__ == "__main__":
    print_dataset_summary()
