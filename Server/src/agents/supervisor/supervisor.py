import json
import re
from src.models.state import GraphState
import time
from src.agents.supervisor.prompts import (
    SUPERVISOR_RESPONSE_SCHEMA
)
from jsonschema import validate, ValidationError
from google.generativeai.generative_models import GenerativeModel

class SupervisorNode:
    """
    Supervisor Node: Coordinates between different components.
    Uses optimized prompts and proper error handling.
    """
    
    def __init__(self, model: GenerativeModel ):
        self.model = model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("================== SUPERVISOR TURN ======================")
        
        try:
            # Global loop guard: cap supervisor turns to prevent recursion overflow
            turns = state.get("supervisor_turns", 0)
            if turns >= 18:
                state["next_step"] = "END"
                state["messages"] = state.get("messages", [])
                state["messages"].append("⚠️ Supervisor: Max turns reached, terminating to avoid recursion.")
                return state
            state["supervisor_turns"] = turns + 1
            # Build optimized prompt with full context
            supervisor_prompt = self.build_supervisor_prompt(state)
            
            # Generate response from Gemini
            response = self._generate_with_retries(supervisor_prompt)
            response_text = response.text.strip()
            

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
            # Hard guard: if we already have extracted symptoms, advance to diagnosis_engine
            try:
                extracted_symptoms = (state.get("symptoms", {}) or {}).get("extracted_symptoms", [])
                if next_step == "symptom_extractor" and extracted_symptoms:
                    next_step = "diagnosis_engine"
                    supervisor_decision["reasoning"] = (
                        "Symptoms already extracted; proceeding to diagnosis_engine to avoid redundant extraction."
                    )
            except Exception:
                pass
            # Loop guard: prevent infinite re-entry into symptom_extractor
            if next_step == "symptom_extractor":
                attempts = state.get("symptom_extractor_attempts", 0)
                # If we've already run symptom extraction once, route forward instead of looping
                if attempts >= 1:
                    symptoms_data = state.get("symptoms", {}) or {}
                    extracted = symptoms_data.get("extracted_symptoms", [])
                    # Prefer diagnosis if we have any structured symptoms
                    if extracted:
                        next_step = "diagnosis_engine"
                        reasoning_override = "Symptom extraction already performed; advancing to diagnosis_engine to avoid loop."
                    else:
                        next_step = "conversation_agent"
                        reasoning_override = "Repeated symptom_extractor without progress; switching to conversation_agent for clarification."
                    supervisor_decision["reasoning"] = reasoning_override
                # Increment attempt counter when we decide to run symptom_extractor again (first time)
                state["symptom_extractor_attempts"] = attempts + 1 if attempts < 1 else attempts
            reasoning = supervisor_decision.get("reasoning", "No reasoning provided")
            updated_plan = supervisor_decision.get("plan", state.get("plan", []))

            # Auto-terminate simple conversation flows to prevent loops
            if next_step == "conversation_agent" and state.get("conversation_output"):
                # If we already produced a conversation output this turn, move to END
                next_step = "END"
            
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
            print("========================================================= CURRENT PLAN =========================================================")
            for i, step in enumerate(updated_plan, 1):
                print(f"  {i}. {step.get('step', 'unknown')} - {step.get('description', '')} [{step.get('status', 'pending')}]")
            print("===================================================================================================================================")
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
        current_step = state.get("current_step", 0)
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
            plan_str = f"**Current Plan** (current at step {current_step}):\n"
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

    def _generate_with_retries(self, prompt: str, retries: int = 3, base_delay: float = 0.75):
        last_err = None
        for attempt in range(retries):
            try:
                return self.model.generate_content(prompt)
            except Exception as e:
                msg = str(e).lower()
                if "429" in msg or "rate" in msg or "quota" in msg or "exhaust" in msg:
                    delay = base_delay * (2 ** attempt)
                    print(f"⏳ Supervisor retry {attempt+1}/{retries} after {delay:.2f}s due to rate limit...")
                    time.sleep(delay)
                    last_err = e
                    continue
                raise
        raise last_err if last_err else RuntimeError("LLM generate failed without exception")


