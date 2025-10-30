from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage

from src.configs.agent_config import GEMINI_MODEL_NAME
from src.agents.nodes.system_prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT

class SupervisorAgentModel:
    def __init__(self):
        self.model = init_chat_model(
            model=f"google_genai:{GEMINI_MODEL_NAME}",
        )


    def invoke(self, prompt: str) -> AIMessage:
        # TODO: what if role assistant
        response = self.model.invoke([
            {"role": "system", "content":SUPERVISOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        return response
