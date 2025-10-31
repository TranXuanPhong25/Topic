"""Recommender Agent - Provide treatment recommendations"""
from src.agents.recommender.config import get_recommender_model
from .recommender import RecommenderNode

def new_recommender_node():
    model = get_recommender_model()
    return RecommenderNode(model)
__all__ = ["RecommenderNode", "new_recommender_node"]
