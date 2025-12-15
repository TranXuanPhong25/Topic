from src.agents.supervisor.config import get_supervisor_model
from .supervisor import SupervisorNode
def new_supervisor_node():
   model = get_supervisor_model()
   return SupervisorNode(model)
__all__ = ["SupervisorNode", "new_supervisor_node"]
