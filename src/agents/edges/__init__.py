"""
Edge definitions for the Medical Diagnostic Graph.
Contains routing logic and edge building functions.
"""

from .routing import IntentRouter, build_graph_edges

__all__ = [
    "IntentRouter",
    "build_graph_edges",
]
