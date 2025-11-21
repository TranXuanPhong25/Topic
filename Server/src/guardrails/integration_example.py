"""
Guardrail Integration Example
Shows how to use different levels of guardrails in the chatbot system
"""

from typing import Optional, List, Dict
from src.guardrails import SimpleGuardrail, IntermediateGuardrail, AdvancedGuardrail


class GuardrailManager:
    """
    Manager to coordinate different guardrail levels.
    Can switch between levels based on requirements.
    """
    
    def __init__(self, level: str = "simple", gemini_api_key: Optional[str] = None):
        """
        Initialize guardrail manager
        
        Args:
            level: "simple", "intermediate", or "advanced"
            gemini_api_key: API key for Gemini (required for intermediate/advanced)
        """
        self.level = level
        
        if level == "simple":
            self.guardrail = SimpleGuardrail()
        elif level == "intermediate":
            self.guardrail = IntermediateGuardrail(gemini_api_key)
        elif level == "advanced":
            self.guardrail = AdvancedGuardrail(gemini_api_key, enable_logging=True)
        else:
            raise ValueError(f"Unknown guardrail level: {level}")
        
        print(f"✅ Guardrail manager initialized with level: {level}")
    
    def validate_input(self, 
                      user_input: str,
                      user_id: str = "anonymous",
                      conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Validate user input before processing
        
        Returns:
            Dict with validation result and modified content if needed
        """
        if self.level == "simple":
            result = self.guardrail.check_input(user_input)
        else:
            result = self.guardrail.check_input(
                user_input, 
                user_id=user_id,
                conversation_history=conversation_history
            )
        
        return {
            "passed": result.passed,
            "action": result.action,
            "modified_content": result.modified_content,
            "severity": result.severity,
            "reason": result.reason
        }
    
    def validate_output(self,
                       bot_response: str,
                       user_input: str,
                       user_id: str = "anonymous",
                       conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Validate bot output before sending to user
        
        Returns:
            Dict with validation result
        """
        if self.level == "simple":
            result = self.guardrail.check_output(bot_response, user_input)
        else:
            result = self.guardrail.check_output(
                bot_response,
                user_input,
                user_id=user_id,
                conversation_history=conversation_history
            )
        
        return {
            "passed": result.passed,
            "action": result.action,
            "modified_content": result.modified_content,
            "severity": result.severity,
            "reason": result.reason
        }
    
    def get_stats(self) -> Dict:
        """Get guardrail statistics"""
        return self.guardrail.get_stats()


# ==================== Usage Examples ====================

def example_simple_guardrail():
    """Example: Using simple guardrail"""
    print("\n" + "="*60)
    print("EXAMPLE: Simple Guardrail (Keyword-Based)")
    print("="*60)
    
    manager = GuardrailManager(level="simple")
    
    test_cases = [
        "Tôi cần đặt lịch khám",  # Normal
        "Tôi bị đau tim, cấp cứu!",  # Emergency
        "Đm chatbot ngu",  # Profanity
        "Thời tiết hôm nay thế nào?",  # Out of scope
    ]
    
    for user_input in test_cases:
        print(f"\nUser: {user_input}")
        result = manager.validate_input(user_input)
        print(f"Result: {result['action']} - {result['reason']}")
        if result['modified_content']:
            print(f"Response: {result['modified_content'][:100]}...")
    
    print(f"\nStats: {manager.get_stats()}")


def example_intermediate_guardrail():
    """Example: Using intermediate guardrail"""
    print("\n" + "="*60)
    print("EXAMPLE: Intermediate Guardrail (NLP + Context)")
    print("="*60)
    
    # Requires Gemini API key
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found. Skipping this example.")
        return
    
    manager = GuardrailManager(level="intermediate", gemini_api_key=api_key)
    
    conversation_history = [
        {"role": "user", "content": "Tôi bị sốt"},
        {"role": "assistant", "content": "Bạn bị sốt bao nhiêu độ?"},
    ]
    
    user_input = "38 độ, có cần uống thuốc gì không?"
    
    print(f"\nConversation history: {len(conversation_history)} messages")
    print(f"User: {user_input}")
    
    result = manager.validate_input(
        user_input,
        user_id="user_123",
        conversation_history=conversation_history
    )
    
    print(f"Intent detected: {result.get('reason', 'N/A')}")
    print(f"Action: {result['action']}")
    
    if result['modified_content']:
        print(f"Response: {result['modified_content']}")
    
    print(f"\nStats: {manager.get_stats()}")


def example_advanced_guardrail():
    """Example: Using advanced guardrail"""
    print("\n" + "="*60)
    print("EXAMPLE: Advanced Guardrail (Multi-Layer + Compliance)")
    print("="*60)
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found. Skipping this example.")
        return
    
    manager = GuardrailManager(level="advanced", gemini_api_key=api_key)
    
    # Test user input
    user_input = "Số điện thoại của tôi là 0912345678. Tôi cần hỏi về triệu chứng."
    
    print(f"\nUser: {user_input}")
    
    result = manager.validate_input(
        user_input,
        user_id="user_advanced_123"
    )
    
    print(f"\nValidation result:")
    print(f"  Passed: {result['passed']}")
    print(f"  Action: {result['action']}")
    print(f"  Severity: {result['severity']}")
    print(f"  Reason: {result['reason']}")
    
    # Test output validation
    bot_response = "Dựa trên triệu chứng, bạn có thể bị cảm cúm. Nên uống paracetamol 500mg."
    
    print(f"\nBot response: {bot_response}")
    
    output_result = manager.validate_output(
        bot_response,
        user_input,
        user_id="user_advanced_123"
    )
    
    print(f"\nOutput validation:")
    print(f"  Passed: {output_result['passed']}")
    print(f"  Action: {output_result['action']}")
    print(f"  Reason: {output_result['reason']}")
    
    if output_result['modified_content']:
        print(f"  Modified: {output_result['modified_content']}")
    
    print(f"\nStats: {manager.get_stats()}")


def example_integration_with_chatbot():
    """Example: Integrating guardrail with chatbot"""
    print("\n" + "="*60)
    print("EXAMPLE: Integration with Chatbot Flow")
    print("="*60)
    
    manager = GuardrailManager(level="simple")
    
    def process_message(user_input: str, user_id: str) -> str:
        """Simulated chatbot message processing with guardrail"""
        
        # 1. Validate input
        input_result = manager.validate_input(user_input, user_id)
        
        if not input_result["passed"]:
            # Block or redirect
            if input_result["action"] == "block":
                return input_result["modified_content"]
            elif input_result["action"] == "redirect":
                return input_result["modified_content"]
        
        # 2. Process with chatbot (simulated)
        bot_response = f"[Chatbot processed: {user_input}] Tôi có thể giúp gì cho bạn?"
        
        # 3. Validate output
        output_result = manager.validate_output(bot_response, user_input, user_id)
        
        if not output_result["passed"]:
            # Use safe fallback
            return output_result["modified_content"] or "Xin lỗi, đã có lỗi xảy ra."
        
        return bot_response
    
    # Test the flow
    test_messages = [
        "Tôi cần đặt lịch khám",
        "Tôi bị đau tim!",
        "Fuck this shit"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = process_message(msg, "user_123")
        print(f"Bot: {response}")
    
    print(f"\nFinal stats: {manager.get_stats()}")


if __name__ == "__main__":
    # Run all examples
    example_simple_guardrail()
    example_intermediate_guardrail()
    example_advanced_guardrail()
    example_integration_with_chatbot()
