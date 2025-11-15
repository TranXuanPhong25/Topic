"""
Synthesis Agent
Synthesizes all results into a comprehensive final report
"""
from .config import get_synthesis_model
from .synthesis import SynthesisNode


def new_synthesis_node():
    model = get_synthesis_model()
    return SynthesisNode(model)


__all__ = ["SynthesisNode", "new_synthesis_node"]
