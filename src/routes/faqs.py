from fastapi import HTTPException
from . import faq_router
from knowledge_base import knowledge_base

# ==================== KNOWLEDGE BASE ENDPOINTS ====================

@faq_router.get("/faq/search")
async def search_faqs(q: str, limit: int = 5):
    """
    Search the FAQ knowledge base.
    
    Args:
        q: Search query
        limit: Maximum number of results (default: 5)
    """
    results = knowledge_base.search_faqs(q, limit=limit)
    
    return {
        "message": "Search completed",
        "query": q,
        "count": len(results),
        "results": results,
    }


@faq_router.get("/faq/categories")
async def get_faq_categories():
    """Get all FAQ categories"""
    categories = knowledge_base.get_all_categories()
    
    return {
        "message": "Categories retrieved",
        "categories": categories,
    }


@faq_router.get("/faq/category/{category}")
async def get_faqs_by_category(category: str):
    """Get all FAQs in a specific category"""
    faqs = knowledge_base.get_faq_by_category(category)
    
    if not faqs:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    return {
        "message": "FAQs retrieved",
        "category": category,
        "count": len(faqs),
        "faqs": faqs,
    }


@faq_router.get("/faq/answer")
async def get_answer(q: str):
    """Get a direct answer to a question"""
    answer = knowledge_base.answer_question(q)
    
    if answer:
        return {
            "message": "Answer found",
            "query": q,
            "answer": answer,
        }
    else:
        return {
            "message": "No direct answer found",
            "query": q,
            "answer": "I don't have specific information about that. Please call us at (555) 123-4567 for assistance.",
        }

