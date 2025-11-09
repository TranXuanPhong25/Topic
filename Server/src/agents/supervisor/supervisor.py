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
        response_text = ""
        try:
            # Build optimized prompt with full context
            if len(state.get("plan", [])) != 0:
                current_step = state.get("current_step", 1) - 1
                if current_step < len(state["plan"]):
                    state["plan"][current_step]["status"] = "completed"
                else:
                    print("⚠️  Current step exceeds plan length; cannot mark as completed.")
                    return state
                    
            supervisor_prompt = self.build_supervisor_prompt(state)
            
            # Generate response from Gemini
            response = self._generate_with_retries(supervisor_prompt)
            response_text = response.text.strip()
            
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
            symptom_extractor_input = supervisor_decision.get("symptom_extractor_input")
            
            # Update state
            state["next_step"] = next_step
            state["plan"] = updated_plan
            
            # Update symptom_extractor_input if supervisor specified it
            if symptom_extractor_input:
                state["symptom_extractor_input"] = symptom_extractor_input
                print(f"📝 Symptom extractor input specified: {symptom_extractor_input[:100]}...")
            
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
        chat_history = state.get("chat_history", "")
        user_input = state.get("input", "")
        current_plan = state.get("plan", [])
        symptoms = state.get("symptoms", "")
        has_image = bool(state.get("image"))
        diagnosis = state.get("diagnosis", {})
        current_step = state.get("current_step", 0)
        # Build context summary
        context_parts = [f"**Chat history**: {chat_history}", f"**User Input**: {user_input}"]
        # print(f"context_parts: {context_parts}  ")

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
    1. **CHECK PLAN STATUS FIRST**: Are ALL steps in the current plan marked as "completed"?
       - If YES and no new user request: Route to END immediately (DO NOT create a new plan)
       - If YES but user has new request: Create new plan for new request
       - If NO: Continue with next pending step
    2. What is the patient trying to achieve?
    3. What information do we already have?
    4. What is the next logical step in the workflow?
    5. If routing to symptom_extractor: Should I specify custom `symptom_extractor_input` to extract specific parts?
    
    ## ⚠️ CRITICAL RULE: DO NOT REPLAN IF PLAN IS COMPLETE
    - If current plan exists and ALL steps have status="completed"
    - AND there is no new user request or issue to address
    - Then you MUST set next_step="END" and keep the existing completed plan
    - DO NOT create a new plan just because you're being called again
    - Only create a new plan if user explicitly asks for something new
    
    ## SPECIAL NOTE FOR SYMPTOM EXTRACTION
    When routing to symptom_extractor, you can optionally include `symptom_extractor_input` in your response.
    - If not specified: symptom_extractor will use full user input + chat history
    - If specified: symptom_extractor will ONLY analyze the text you provide
    - **IMPORTANT**: You can combine relevant parts from BOTH current input AND chat_history
    - Use this to filter out non-symptom parts (e.g., greetings, appointments, FAQs)
    - Use this to consolidate symptoms mentioned across multiple conversation turns
    
    Examples:
    1. Filter non-medical: Input "Hello! I have fever. Can you check your hours?" → symptom_extractor_input: "I have fever"
    2. Combine history: Chat: "User: I had mild headache yesterday" + Input: "Now it's severe with nausea" 
       → symptom_extractor_input: "Mild headache yesterday, now severe with nausea"
    3. Focus on new info: Chat has previous symptoms, Input adds new ones
       → symptom_extractor_input: "Previous: [old symptoms]. New: [new symptoms]"
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


