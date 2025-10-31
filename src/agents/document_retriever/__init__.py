"""Document Retriever Agent - Retrieve relevant medical documents"""
from src.agents.document_retriever.config import get_document_retriever_model
from .document_retriever import DocumentRetrieverNode

def new_document_retriever_node():
    model = get_document_retriever_model()
    return DocumentRetrieverNode(model)

__all__ = ["DocumentRetrieverNode", "new_document_retriever_node"]
