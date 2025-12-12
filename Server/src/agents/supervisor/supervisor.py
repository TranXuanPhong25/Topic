import json
import re
from typing import Any, List
from src.models.state import GraphState
from src.configs.agent_config import SystemMessage, HumanMessage, AIMessage, BaseMessage
from src.agents.supervisor.prompts import (
    COMPACT_SUPERVISOR_PROMPT,
    SUPERVISOR_RESPONSE_SCHEMA,
    SUPERVISOR_SYSTEM_PROMPT
)
from src.agents.utils import build_messages_with_history
from src.agents.utils.message_builder import extract_text_from_gemini_message
from jsonschema import validate, ValidationError

# Emergency keywords for fast-path routing (Vietnamese & English)
EMERGENCY_KEYWORDS = {
    # Vietnamese
    "đau ngực", "khó thở", "không thở được", "ngất", "bất tỉnh", "co giật", 
    "chảy máu nhiều", "đột quỵ", "liệt", "tê nửa người", "sốc phản vệ",
    "ngộ độc", "tự tử", "muốn chết", "cấp cứu", "khẩn cấp", "nguy hiểm",
    "đau dữ dội", "không cử động được", "mất ý thức",
    # English  
    "chest pain", "can't breathe", "difficulty breathing", "unconscious",
    "seizure", "stroke", "paralysis", "severe bleeding", "anaphylaxis",
    "poisoning", "suicide", "want to die", "emergency", "heart attack",
    "severe pain", "loss of consciousness", "can't move"
}

def _is_emergency_input(text: str) -> bool:
    """Check if user input contains emergency keywords"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

class SupervisorNode:
    """
    Supervisor Node: Coordinates between different components.
    Uses optimized prompts and proper error handling.
    """
    
    def __init__(self, model: Any):
        self.model = model
    
    def __call__(self, state: "GraphState") -> "GraphState":
        print("================== SUPERVISOR TURN ======================")
        response_text = ""
        
        # FAST PATH: Emergency keyword detection - skip LLM, route directly
        user_input = state.get("input", "")
        if _is_emergency_input(user_input) and not state.get("plan"):
            print("🚨 EMERGENCY DETECTED - Fast-path routing to symptom_extractor → diagnosis_engine")
            state["next_step"] = "symptom_extractor"
            state["plan"] = [
                {"step": "symptom_extractor", "description": "Extract emergency symptoms", "status": "not_started", 
                 "goal": "Extract all symptoms from emergency situation", "context": "EMERGENCY - prioritize severity assessment"},
                {"step": "diagnosis_engine", "description": "Emergency diagnosis and risk assessment", "status": "not_started",
                 "goal": "Assess emergency severity and provide immediate guidance", "context": "EMERGENCY case - be conservative, recommend immediate care"},
                {"step": "synthesis", "description": "Generate emergency response", "status": "not_started",
                 "goal": "Provide clear emergency instructions", "context": "EMERGENCY - include 115/911 guidance"}
            ]
            state["current_step"] = 0
            print("🚨 Emergency plan created - bypassing LLM supervisor")
            return state
        
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
            if len(state.get("plan", [])) != 0:
                current_step = state.get("current_step", 1) - 1
                if current_step < len(state["plan"]):
                    state["plan"][current_step]["status"] = "completed"
                else:
                    print("⚠️  Current step exceeds plan length; cannot mark as completed.")
                    return state
                    
            supervisor_prompt = self.build_supervisor_prompt(state)
            
            # Build messages with chat history for full context
            messages = build_messages_with_history(
                system_prompt=SUPERVISOR_SYSTEM_PROMPT,
                current_prompt=supervisor_prompt,
                chat_history=state.get("chat_history", [])
            )
            response = self.model.invoke(messages)
            response_text = response.content.strip()
            
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
            symptom_extractor_input = supervisor_decision.get("symptom_extractor_input")
            
            # Update state
            state["next_step"] = next_step
            state["plan"] = updated_plan
            
            # Update symptom_extractor_input if supervisor specified it
            if symptom_extractor_input:
                state["symptom_extractor_input"] = symptom_extractor_input
                print(f"📝 Symptom extractor input specified: {symptom_extractor_input[:100]}...")
            
            # Add to messages for tracking
   
            print(f"💭 Reasoning: {reasoning}")
            print("******************************************** CURRENT PLAN ********************************************")
            for i, step in enumerate(updated_plan, 1):
                print(f"  {i}. {step.get('step', 'unknown')} - {step.get('description', '')} [{step.get('status', 'not_started')}]")
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
        chat_history_raw = state.get("chat_history", [])
        user_input = state.get("input", "")
        current_plan = state.get("plan", [])
        symptoms = state.get("symptoms", "")
        has_image = bool(state.get("image"))
        diagnosis = state.get("diagnosis", {})
        current_step = state.get("current_step", 0)
        
        # Format chat history into readable message list
        chat_history_formatted = ""
        if chat_history_raw:
            messages = []
            for msg in chat_history_raw:
                role = "User" if msg.get("role") == "user" else "Assistant"
                text = extract_text_from_gemini_message(msg)
                if text:
                    messages.append(f"{role}: {text}")
            chat_history_formatted = "\n".join(messages)
        
        # Build context summary
        context_parts = []
        if chat_history_formatted:
            context_parts.append(f"**Previous Conversation**:\n{chat_history_formatted}")
            # If we have chat history AND a plan that's started, check if input is new
            if current_plan and current_step > 0:
                # Input has already been processed - don't show as "new" request
                context_parts.append(f"**Original Request** (already processed): {user_input}")
            else:
                # First time or new conversation
                context_parts.append(f"**Current User Input**: {user_input}")
        else:
            # No chat history - this is the first/only input
            context_parts.append(f"**Current User Input**: {user_input}")
        # print(f"context_parts: {context_parts}  ")

        if symptoms:
            context_parts.append(f"**Symptoms**: {symptoms}")

        if has_image:
            image_type = state.get("image_type", "unknown")
            is_diagnostic = state.get("is_diagnostic_image", True)
            image_intent = state.get("image_analysis_intent", "")
            
            if image_type == "document":
                context_parts.append(f"**Image Provided**: Yes (type=document, is_diagnostic={is_diagnostic})")
                context_parts.append(f"**⚠️ IMPORTANT**: This is a DOCUMENT image (prescription/test result), NOT a medical image for diagnosis. Route to synthesis, NOT diagnosis_engine.")
                if image_intent:
                    context_parts.append(f"**User intent**: {image_intent}")
            elif image_type == "general":
                context_parts.append(f"**Image Provided**: Yes (type=general, is_diagnostic=False)")
                context_parts.append(f"**⚠️ IMPORTANT**: This is a general non-medical image. Image analyzer already handled it. Consider routing to END.")
            elif image_type == "medical":
                context_parts.append(f"**Image Provided**: Yes (type=medical, is_diagnostic=True - proceed with diagnosis workflow)")
            else:
                context_parts.append(f"**Image Provided**: Yes (type={image_type}, is_diagnostic={is_diagnostic})")

        if diagnosis:
            context_parts.append(
                f"**Diagnosis Available**: Yes - {diagnosis.get('primary_diagnosis', 'Not specified')}")

        # Format current plan
        if current_plan:
            plan_str = f"**Current Plan** (current at step {current_step-1}):\n"
            for i, step in enumerate(current_plan, 0):
                status = step.get("status", "not_started")
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
    1. **UNDERSTAND CONTEXT**: Review "Previous Conversation" (User/Assistant messages) to understand history
    2. **CHECK REQUEST TYPE**: 
       - If you see "**Original Request** (already processed)": This is NOT a new request, plan is handling it
       - If you see "**Current User Input**": This is a new/first request
    3. **CHECK PLAN STATUS**: Are ALL steps in the current plan marked as "completed"?
       - If YES and request shows "already processed": Route to END immediately (DO NOT create a new plan)
       - If YES and you see new "Current User Input": Create new plan for new request
       - If NO: Continue with next not_started step
    4. What is the patient trying to achieve?
    5. What information do we already have?
    6. What is the next logical step in the workflow?
    7. If routing to symptom_extractor: Should I specify custom `symptom_extractor_input` to extract specific parts?
    
    ## ⚠️ CRITICAL RULE: DO NOT REPLAN IF PLAN IS COMPLETE
    - If current plan exists and ALL steps have status="completed"
    - AND you see "**Original Request** (already processed)" (NOT "Current User Input")
    - Then you MUST set next_step="END" and keep the existing completed plan
    - DO NOT create a new plan - the work is done!
    - Only create a new plan if you see fresh "**Current User Input**" (without "already processed")
    
    ## SPECIAL NOTE FOR SYMPTOM EXTRACTION
    When routing to symptom_extractor, you can optionally include `symptom_extractor_input` in your response.
    - If not specified: symptom_extractor will use full user input + chat history
    - If specified: symptom_extractor will ONLY analyze the text you provide
    - **IMPORTANT**: You can combine relevant parts from BOTH "Previous Conversation" AND "Current User Input"
    - Use this to filter out non-symptom parts (e.g., greetings, appointments, FAQs)
    - Use this to consolidate symptoms mentioned across multiple conversation turns
    - Example: User said "I have fever" earlier, now says "and cough too" → combine to "fever and cough"
    
    Examples:
    1. Filter non-medical: Input "Hello! I have fever. Can you check your hours?" → symptom_extractor_input: "I have fever"
    2. Combine history: Chat: "User: I had mild headache yesterday" + Input: "Now it's severe with nausea" 
       → symptom_extractor_input: "Mild headache yesterday, now severe with nausea"
    3. Focus on new info: Chat has previous symptoms, Input adds new ones
       → symptom_extractor_input: "Previous: [old symptoms]. New: [new symptoms]"
    """
        return prompt

