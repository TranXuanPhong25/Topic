from src.agents.diagnosis_critic.config import get_diagnosis_critic_model
from .diagnosis_critic import DiagnosisCriticNode
def new_diagnosis_crictic_node():
    model = get_diagnosis_critic_model()
    return DiagnosisCriticNode(model)
__all__ = ["DiagnosisCriticNode", "new_diagnosis_crictic_node"]
