import json
import re
from src.models.state import GraphState
from .system_prompts.supervisor_prompt import (
    SUPERVISOR_RESPONSE_SCHEMA
)
from jsonschema import validate, ValidationError

class SupervisorNode:
    """
    Supervisor Node: Coordinates between different components.
    Uses optimized prompts and proper error handling.
    """
    
    def __init__(self, model):
        self.model = model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("🎯 Supervisor: Coordinating workflow...")
        
        try:
            # Build optimized prompt with full context
            supervisor_prompt = self.build_supervisor_prompt(state)
            
            # Generate response from Gemini
            response = self.model.invoke(supervisor_prompt)
            response_text = response.text.strip()
            
            print(f"📋 Supervisor Response: {response_text[:200]}...")
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Parse JSON
            supervisor_decision = json.loads(json_text)
            
            # Validate against schema
            try:
                validate(instance=supervisor_decision, schema=SUPERVISOR_RESPONSE_SCHEMA)
            except ValidationError as ve:
                print(f"⚠️  Validation warning: {ve.message}")
                # Continue with best effort
            
            # Extract decisions
            next_step = supervisor_decision.get("next_step", "END")
            reasoning = supervisor_decision.get("reasoning", "No reasoning provided")
            updated_plan = supervisor_decision.get("plan", state.get("plan", []))
            
            # Update state
            state["next_step"] = next_step
            state["plan"] = updated_plan
            
            # Add to messages for tracking
            message = f"✅ Supervisor: Next step → {next_step} | Reason: {reasoning[:100]}"
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append(message)
            
            print(f"✅ Decision: {next_step}")
            print(f"💭 Reasoning: {reasoning}")
            print(f"📝 Updated plan: {len(updated_plan)} steps")
            
            return state
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response text: {response_text}")
            # Fallback: try to extract next_step manually
            return self._fallback_decision(state, response_text)
            
        except Exception as e:
            print(f"❌ Supervisor Error: {e}")
            return self._fallback_decision(state, str(e))
    
    def _fallback_decision(self, state: "GraphState", error_info: str) -> "GraphState":
        """
        Fallback decision when primary parsing fails.
        Uses heuristics based on current state.
        """
        print("⚠️  Using fallback decision logic...")
        
        intent = state.get("intent", "not_classified")
        has_image = bool(state.get("image"))
        has_diagnosis = bool(state.get("diagnosis"))
        current_plan = state.get("plan", [])
        
        # Heuristic-based decision
        if intent == "appointment":
            next_step = "appointment_scheduler"
        elif intent == "general_question":
            next_step = "conversation_agent"
        elif has_image and not any(s.get("step") == "image_analyzer" for s in current_plan):
            next_step = "image_analyzer"
        elif intent == "medical_diagnosis" and not has_diagnosis:
            next_step = "diagnosis_engine"
        elif has_diagnosis:
            next_step = "recommender"
        else:
            next_step = "conversation_agent"
        
        state["next_step"] = next_step
        state["messages"] = state.get("messages", [])
        state["messages"].append(f"⚠️  Supervisor: Fallback decision → {next_step}")
        
        print(f"🔄 Fallback decision: {next_step}")
        return state

    def build_supervisor_prompt(self, state: GraphState) -> str:
        """
        Build the supervisor prompt with current state context.

        Args:
            state: Current graph state containing input, plan, symptoms, etc.

        Returns:
            Complete prompt string ready for LLM
        """
        user_input = state.get("input", "")
        current_plan = state.get("plan", [])
        intent = state.get("intent", "not_classified")
        symptoms = state.get("symptoms", "")
        has_image = bool(state.get("image"))
        diagnosis = state.get("diagnosis", {})
        messages = state.get("messages", [])

        # Build context summary
        context_parts = []
        context_parts.append(f"**User Input**: {user_input}")
        context_parts.append(f"**Detected Intent**: {intent}")

        if symptoms:
            context_parts.append(f"**Symptoms**: {symptoms}")

        if has_image:
            context_parts.append(f"**Image Provided**: Yes (requires analysis)")

        if diagnosis:
            context_parts.append(
                f"**Diagnosis Available**: Yes - {diagnosis.get('primary_diagnosis', 'Not specified')}")

        if messages:
            recent_messages = messages[-3:] if len(messages) > 3 else messages
            context_parts.append(f"**Recent Actions**: {', '.join(recent_messages)}")

        # Format current plan
        if current_plan:
            plan_str = "**Current Plan**:\n"
            for i, step in enumerate(current_plan, 1):
                status = step.get("status", "pending")
                plan_str += f"  {i}. {step.get('step', 'unknown')} - {step.get('description', '')} [{status}]\n"
        else:
            plan_str = "**Current Plan**: None (you must create one)"

        context_summary = "\n".join(context_parts)

        # Build final prompt
        prompt = f"""

    ## CURRENT SITUATION
    {context_summary}

    {plan_str}

    ## YOUR TASK
    Analyze the current situation and decide the next step. Think step-by-step:
    1. What is the patient trying to achieve?
    2. What information do we already have?
    3. What is the next logical step in the workflow?
    4. Which agent is best suited for this step?

    Respond with ONLY valid JSON (no markdown, no comments):
    {{
      "next_step": "<agent_name or END>",
      "reasoning": "<your step-by-step thinking process>",
      "plan": [
        {{"step": "agent_name", "description": "what this agent will do", "status": "current|pending|completed|skipped"}}
      ]
    }}
    """

        return prompt


