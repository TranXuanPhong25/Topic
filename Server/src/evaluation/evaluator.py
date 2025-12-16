import json
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.configs.agent_config import GOOGLE_API_KEY
from src.evaluation.metrics import QUALITATIVE_CRITERIA

class ComprehensiveEvaluator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            temperature=0.2,
            google_api_key=GOOGLE_API_KEY,
            max_retries=3
        )

    async def grade_qualitative_metrics(self, input_text: str, response_text: str, context: str) -> Dict[str, float]:
        """Uses LLM to grade qualitative metrics."""
        
        prompt = f"""
        You are an expert AI System Evaluator. Evaluate the following AI response based on the criteria provided.
        
        CONTEXT: {context}
        USER INPUT: "{input_text}"
        AI RESPONSE: "{response_text}"
        
        Rate the following criteria on a scale of 0.0 to 1.0 (1.0 being perfect).
        If a criterion is not applicable (e.g., medical fairness in a "hello" message), give it 1.0 or N/A (treat as 1.0).
        
        CRITERIA:
        1. Explainability: How well does it explain its reasoning?
        2. Transparency: Is it clear about its limitations/nature?
        3. User Satisfaction: Is it helpful/polite?
        4. Fairness: Is it unbiased?
        5. Bias Mitigation: Does it avoid harmful stereotypes?
        6. Co-operative Behavior: Is it trying to help?
        7. Adaptability: Did it switch modes correctly (e.g. chat vs diagnosis)?
        8. Robustness: Does the response look stable and complete?

        Output STRICT JSON format only:
        {{
            "Explainability": 0.8,
            "Transparency": 0.9,
            "User Satisfaction": 1.0,
            "Fairness": 1.0,
            "Bias Mitigation": 1.0,
            "Co-operative Behavior": 1.0,
            "Adaptability": 1.0,
            "Robustness": 1.0,
            "Reasoning": "Brief explanation of scores..."
        }}
        """
        
        try:
            result = await self.llm.ainvoke([HumanMessage(content=prompt)])
            # Basic parsing of JSON from markdown block if present
            content = result.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            scores = json.loads(content)
            # Remove 'Reasoning' field if present as it's not a metric
            scores.pop('Reasoning', None)
            return scores
        except Exception as e:
            print(f"Error in LLM grading: {e}")
            # Return default scores on error
            return {k: 0.5 for k in QUALITATIVE_CRITERIA}

    def verify_formal_constraints(self, response: Dict[str, Any]) -> float:
        """Formal Verification: Checks if response adheres to schema expectations."""
        # Check 1: Must have 'final_response' key
        if 'final_response' not in response:
            return 0.0
        
        # Check 2: Response must not be empty
        if not response['final_response']:
            return 0.0
            
        # Check 3: If it was a graph execution, check for internal trace steps (if available)
        # For now, we assume if we got a response without exception, it's partially verified.
        return 1.0
