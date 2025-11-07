"""
DocumentRetriever Node: Performs information augmentation from knowledge sources.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..medical_diagnostic_graph import GraphState

class DocumentRetrieverNode:
    """
    DocumentRetriever Node: Performs information augmentation.
    
    Queries Vector Database (embeddings) and Knowledge Graph (KB).
    """
    
    def __init__(self, knowledge_base):
        """
        Initialize the DocumentRetriever node.
        
        Args:
            knowledge_base: FAQ knowledge base for document retrieval
        """
        self.knowledge_base = knowledge_base
    
    def __call__(self, state: "GraphState") -> "GraphState":
        """
        Execute the document retriever logic.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated graph state with retrieved documents
        """
        print("📚 DocumentRetriever: Retrieving relevant medical documents...")
        
        diagnosis = state.get("diagnosis", {})
        primary_diagnosis = diagnosis.get("primary_diagnosis", "")
        
        try:
            # Search knowledge base for relevant information
            # In real implementation, this would query vector DB + KG
            search_results = self.knowledge_base.search_faqs(primary_diagnosis, limit=5)
            
            # Format as documents
            documents = [
                {
                    "source": "FAQ Database",
                    "content": result.get("answer", ""),
                    "relevance": 0.9
                }
                for result in search_results
            ]
            
            # Add medical knowledge (simulated)
            documents.append({
                "source": "Medical Knowledge Graph",
                "content": f"Thông tin y khoa về: {primary_diagnosis}",
                "relevance": 0.8
            })
            
            state["retrieved_documents"] = documents
            state["current_step"] +=1

            print(f"Retrieved {len(documents)} relevant documents")
            
        except Exception as e:
            print(f"DocumentRetriever error: {str(e)}")
            state["retrieved_documents"] = []
        
        return state
