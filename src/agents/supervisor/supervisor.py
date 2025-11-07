import json
import re
from src.models.state import GraphState
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
        response_text = ""
        try:
            # Build optimized prompt with full context
            if len(state.get("plan", [])) != 0:
                state["plan"][state.get("current_step",1)-1]["status"] = "completed"
            supervisor_prompt = self.build_supervisor_prompt(state)

            response = self.model.generate_content(supervisor_prompt)
            response_text = response.text.strip()
            
            print(response_text)
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*(\{.*?})\s*```', response_text, re.DOTALL)
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
   
            print(f"✅ Decision: {next_step}")
            print(f"💭 Reasoning: {reasoning}")
            print(f"📝 Updated plan: {len(updated_plan)} steps")
            print("******************************************** CURRENT PLAN ********************************************")
            for i, step in enumerate(updated_plan, 1):
                print(f"  {i}. {step.get('step', 'unknown')} - {step.get('description', '')} [{step.get('status', 'pending')}]")
            print("*******************************************************************************************************")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response text: {response_text}")
            
        except Exception as e:
            print(f"❌ Supervisor Error: {e}")
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
        symptoms = state.get("symptoms", "")
        has_image = bool(state.get("image"))
        diagnosis = state.get("diagnosis", {})
        current_step = state.get("current_step", 0)
        # Build context summary
        context_parts = [f"**User Input**: {user_input}"]

        if symptoms:
            context_parts.append(f"**Symptoms**: {symptoms}")

        if has_image:
            context_parts.append(f"**Image Provided**: Yes (requires analysis)")

        if diagnosis:
            context_parts.append(
                f"**Diagnosis Available**: Yes - {diagnosis.get('primary_diagnosis', 'Not specified')}")

        # Format current plan
        if current_plan:
            plan_str = f"**Current Plan** (current at step {current_step}):\n"
            for i, step in enumerate(current_plan, 0):
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
    """
    # 4. Which agent is best suited for this step?
    #
    # Respond with ONLY valid JSON (no markdown, no comments):
    # {{
    #   "next_step": "<agent_name or END>",
    #   "reasoning": "<your step-by-step thinking process>",
    #   "plan": [
    #     {{"step": "agent_name", "description": "what this agent will do", "status": "current|pending|completed|skipped"}}
    #   ]
    # }}

        return prompt


