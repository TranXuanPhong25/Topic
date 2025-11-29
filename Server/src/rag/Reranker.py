"""
Document Reranker for RAG System
Reorders retrieved documents using cross-encoder models for improved relevance.
"""

from typing import List, Tuple
from dataclasses import dataclass
from flashrank import Ranker, RerankRequest


@dataclass
class RankedDocument:
    """Represents a document with its reranking score"""
    content: str
    metadata: dict
    score: float
    original_index: int


class DocumentReranker:
    """
    Reranks retrieved documents using cross-encoder models.
    
    Uses FlashRank for efficient, lightweight reranking without GPU requirements.
    The reranker assigns a relevance score to each document based on how well
    it matches the query, allowing us to reorder documents for better results.
    """
    
    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2"):
        """
        Initialize the document reranker.
        
        Args:
            model_name: Name of the cross-encoder model to use for reranking.
                       Default is a lightweight MSMARCO model.
        """
        try:
            self.ranker = Ranker(model_name=model_name)
            self.model_name = model_name
            print(f"✓ Reranker initialized with model: {model_name}")
        except Exception as e:
            print(f"⚠️ Failed to initialize reranker: {e}")
            print("   Continuing without reranking capability")
            self.ranker = None
    
    def rerank(
        self, 
        query: str, 
        documents: List[any],
        top_k: int = None
    ) -> List[any]:
        """
        Rerank documents based on their relevance to the query.
        
        Args:
            query: The search query
            documents: List of LangChain Document objects to rerank
            top_k: Number of top documents to return (None returns all)
            
        Returns:
            List of documents reordered by relevance score
        """
        if not self.ranker or not documents:
            return documents
        
        try:
            # Prepare passages for reranking
            passages = []
            for i, doc in enumerate(documents):
                # Extract text content from document
                text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                passages.append({
                    "id": i,
                    "text": text,
                    "meta": doc.metadata if hasattr(doc, 'metadata') else {}
                })
            
            # Create rerank request
            rerank_request = RerankRequest(
                query=query,
                passages=passages
            )
            
            # Perform reranking
            results = self.ranker.rerank(rerank_request)
            
            # Reorder original documents based on reranking results
            reranked_docs = []
            for result in results:
                original_idx = result['id']
                reranked_docs.append(documents[original_idx])
            
            # Return top_k documents if specified
            if top_k is not None:
                return reranked_docs[:top_k]
            
            return reranked_docs
            
        except Exception as e:
            print(f"⚠️ Reranking failed: {e}, returning original order")
            return documents
    
    def rerank_with_scores(
        self,
        query: str,
        documents: List[any],
        top_k: int = None
    ) -> List[Tuple[any, float]]:
        """
        Rerank documents and return them with their relevance scores.
        
        Args:
            query: The search query
            documents: List of LangChain Document objects to rerank
            top_k: Number of top documents to return (None returns all)
            
        Returns:
            List of tuples (document, score) ordered by relevance
        """
        if not self.ranker or not documents:
            return [(doc, 0.0) for doc in documents]
        
        try:
            # Prepare passages for reranking
            passages = []
            for i, doc in enumerate(documents):
                text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                passages.append({
                    "id": i,
                    "text": text,
                    "meta": doc.metadata if hasattr(doc, 'metadata') else {}
                })
            
            # Create rerank request
            rerank_request = RerankRequest(
                query=query,
                passages=passages
            )
            
            # Perform reranking
            results = self.ranker.rerank(rerank_request)
            
            # Create list of (document, score) tuples
            reranked_with_scores = []
            for result in results:
                original_idx = result['id']
                score = result.get('score', 0.0)
                reranked_with_scores.append((documents[original_idx], score))
            
            # Return top_k documents if specified
            if top_k is not None:
                return reranked_with_scores[:top_k]
            
            return reranked_with_scores
            
        except Exception as e:
            print(f"⚠️ Reranking failed: {e}, returning original order with zero scores")
            return [(doc, 0.0) for doc in documents]


def create_reranker(model_name: str = "ms-marco-MiniLM-L-12-v2") -> DocumentReranker:
    """
    Factory function to create a DocumentReranker instance.
    
    Args:
        model_name: Name of the cross-encoder model to use
        
    Returns:
        Configured DocumentReranker instance
    """
    return DocumentReranker(model_name)

