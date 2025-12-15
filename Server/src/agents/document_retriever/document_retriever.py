"""
DocumentRetriever Agent: Performs information augmentation from knowledge sources using RAG pipeline.

This agent:
- Receives input queries from the supervisor
- Refines and optimizes queries for medical document retrieval
- Uses RAG pipeline to retrieve relevant documents
- Synthesizes information from multiple sources
- Returns structured results with citations and confidence assessments
"""
from typing import TYPE_CHECKING, Dict, Any, Optional
import logging
import json

from src.configs.agent_config import SystemMessage, HumanMessage
from .rag.Retrieve import RAGPipeline
from .config import get_document_retriever_model
from .prompts import (
    DOCUMENT_RETRIEVER_SYSTEM_PROMPT,
    build_document_retrieval_prompt,
)

if TYPE_CHECKING:
    from src.models.state import GraphState

LOGGER = logging.getLogger(__name__)


class DocumentRetrieverNode:
    def __init__(self, llm_model=None):
        # Initialize LLM for query analysis and synthesis
        self.llm = llm_model or get_document_retriever_model()
        
        # Initialize RAG pipeline
        try:
            self.pipeline = RAGPipeline.from_existing_index()
            print("DocumentRetriever: RAG pipeline initialized")
        except Exception as e:
            LOGGER.error(f"Failed to initialize RAG pipeline: {e}")
            self.pipeline = None
        
        print("DocumentRetrieverNode initialized as agent")
    
    def _get_current_goal(self, state: "GraphState") -> str:
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return ""
        
        current_plan_step = plan[current_step_index]
        goal = current_plan_step.get("goal", "")
        
        if goal:
            print(f"Current Goal: {goal}")
        
        return goal
    
    def _get_current_context(self, state: "GraphState") -> dict:
        plan = state.get("plan", [])
        current_step_index = state.get("current_step", 0)
        
        if not plan or current_step_index >= len(plan):
            return {"context": "", "user_context": ""}
        
        current_plan_step = plan[current_step_index]
        context = current_plan_step.get("context", "")
        user_context = current_plan_step.get("user_context", "")
        
        if context:
            print(f"Context: {context[:100]}...")
        if user_context:
            print(f"User Context: {user_context[:100]}...")
        
        return {"context": context, "user_context": user_context}
    
    def _format_symptoms(self, symptoms: Dict[str, Any]) -> str:
        if not symptoms:
            return ""
        
        parts = []
        symptom_list = symptoms.get("symptoms", [])
        if symptom_list:
            symptom_names = [s.get("name", "") for s in symptom_list if s.get("name")]
            if symptom_names:
                parts.append(f"Triệu chứng: {', '.join(symptom_names)}")
        
        chief_complaint = symptoms.get("chief_complaint", "")
        if chief_complaint:
            parts.append(f"Lý do khám: {chief_complaint}")
        
        return "\n".join(parts)
    
    def _format_diagnosis(self, diagnosis: Dict[str, Any]) -> str:
        if not diagnosis:
            return ""
        
        parts = []
        primary = diagnosis.get("primary_diagnosis", "")
        if primary:
            parts.append(f"Chẩn đoán chính: {primary}")
        
        differentials = diagnosis.get("differential_diagnoses", [])
        if differentials:
            diff_names = [d.get("condition", "") for d in differentials[:3] if d.get("condition")]
            if diff_names:
                parts.append(f"Chẩn đoán phân biệt: {', '.join(diff_names)}")
        
        return "\n".join(parts)
    
    def _format_retrieved_docs(self, docs: list) -> str:
        if not docs:
            return ""
        
        formatted = []
        for idx, doc in enumerate(docs, 1):
            source = doc.get("source", "Unknown")
            author = doc.get("author", "Unknown")
            page = doc.get("page", "N/A")
            content = doc.get("content", "")
            
            formatted.append(
                f"[Nguồn {idx}]\n"
                f"- Tiêu đề: {source}\n"
                f"- Tác giả: {author}\n"
                f"- Trang: {page}\n"
                f"- Nội dung: {content[:500]}..."
            )
        
        return "\n\n---\n\n".join(formatted)

    def _build_query(self, state: "GraphState") -> str:
        parts = []
        
        # Add user input
        user_input = state.get("input", "")
        if user_input:
            parts.append(user_input)
        
        # Add symptoms if available
        symptoms = state.get("symptoms", {})
        if symptoms:
            symptom_list = symptoms.get("symptoms", [])
            if symptom_list:
                symptom_text = ", ".join([s.get("name", "") for s in symptom_list if s.get("name")])
                if symptom_text:
                    parts.append(f"Triệu chứng: {symptom_text}")
        
        # Add diagnosis if available
        diagnosis = state.get("diagnosis", {})
        if diagnosis:
            primary = diagnosis.get("primary_diagnosis", "")
            if primary:
                parts.append(f"Chẩn đoán: {primary}")
            
            differentials = diagnosis.get("differential_diagnoses", [])
            if differentials:
                diff_text = ", ".join([d.get("condition", "") for d in differentials[:3] if d.get("condition")])
                if diff_text:
                    parts.append(f"Chẩn đoán phân biệt: {diff_text}")
        
        return ". ".join(parts) if parts else "medical information"
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        try:
            # Try direct JSON parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Return empty dict if all parsing fails
            LOGGER.warning("Failed to parse LLM response as JSON")
            return {}
    
    def _synthesize_with_llm(
        self,
        query: str,
        documents: list,
        goal: str,
        context: str,
        symptoms_str: str,
        diagnosis_str: str
    ) -> Dict[str, Any]:

        try:
            # Format documents for LLM
            docs_formatted = self._format_retrieved_docs(documents)
            
            # Build prompt
            prompt = build_document_retrieval_prompt(
                query=query,
                context=context,
                goal=goal,
                symptoms=symptoms_str,
                diagnosis=diagnosis_str,
                retrieved_docs=docs_formatted
            )
            
            # Call LLM for synthesis
            messages = [
                SystemMessage(content=DOCUMENT_RETRIEVER_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            synthesis_result = self._parse_json_response(response_text)
            
            print(f"LLM synthesis completed")
            return synthesis_result
            
        except Exception as e:
            LOGGER.error(f"LLM synthesis error: {e}")
            return {}

    def __call__(self, state: "GraphState") -> "GraphState":
        print("\n📚 === DOCUMENT RETRIEVER AGENT STARTED ===")
        
        # Get caller information
        caller = state.get("retriever_caller") or "supervisor"
        
        if caller not in ["supervisor", "diagnosis_engine", "diagnosis_critic", "recommender"]:
            print(f"⚠️ Invalid caller '{caller}', defaulting to supervisor")
            caller = "supervisor"
            state["retriever_caller"] = caller
        
        goal = self._get_current_goal(state)
        context_data = self._get_current_context(state)
        context = context_data.get("context", "")
        
        # Format available information
        symptoms = state.get("symptoms", {})
        diagnosis = state.get("diagnosis", {})
        symptoms_str = self._format_symptoms(symptoms)
        diagnosis_str = self._format_diagnosis(diagnosis)
        
        
        try:
            # Use retriever_query if provided, otherwise build from state
            query = state.get("retriever_query") or self._build_query(state)
            print(f"Search query: {query[:100]}...")
            
            # Invoke RAG pipeline
            result = self.pipeline.invoke(query, k=10, rerank_top_k=5)
            
            # Debug: Log the result structure
            print(f"RAG result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Extract documents and format for state
            context_docs = result.get("context_docs", [])
            documents = []
            
            # Ensure context_docs is not None and is iterable
            if not context_docs:
                context_docs = []
                print("⚠️ No context_docs found in RAG result")
            else:
                print(f"📄 Found {len(context_docs)} context documents")
                if context_docs and len(context_docs) > 0:
                    first_doc = context_docs[0]
                    print(f"🔍 First doc type: {type(first_doc)}")
                    if hasattr(first_doc, '__dict__'):
                        print(f"🔍 First doc attributes: {list(first_doc.__dict__.keys())}")
                    elif isinstance(first_doc, dict):
                        print(f"🔍 First doc keys: {list(first_doc.keys())}")
            
            for doc in context_docs:
                try:
                    # Handle both Document objects and dict structures
                    if hasattr(doc, 'metadata') and hasattr(doc, 'page_content'):
                        # LangChain Document object
                        metadata = doc.metadata or {}
                        content = doc.page_content
                    elif isinstance(doc, dict):
                        # Dictionary structure
                        metadata = doc.get("meta", {})
                        content = doc.get("text", "")
                    else:
                        # Fallback for unknown structure
                        print(f"⚠️ Unknown document structure: {type(doc)}")
                        metadata = {}
                        content = str(doc)
                    
                    documents.append({
                        "source": metadata.get("title", "Medical Document"),
                        "author": metadata.get("author", "Unknown"),
                        "page": metadata.get("page", "N/A"),
                        "content": content,
                        "relevance": 0.9  # Reranked docs are high relevance
                    })
                except Exception as doc_error:
                    LOGGER.warning(f"Error processing document: {doc_error}")
                    print(f"⚠️ Error processing document: {doc_error}")
                    continue
            
            # Get RAG pipeline's answer
            rag_answer = result.get("answer", "")
            english_query = result.get("english_query", "")
            
            print(f"✅ Retrieved {len(documents)} relevant documents")
            print(f"📝 RAG answer generated ({len(str(rag_answer))} chars)")
            
            # Use LLM to synthesize information
            synthesis_result = self._synthesize_with_llm(
                query=query,
                documents=documents,
                goal=goal,
                context=context,
                symptoms_str=symptoms_str,
                diagnosis_str=diagnosis_str
            )
            
            # Update state with results
            state["retrieved_documents"] = documents
            state["rag_answer"] = str(rag_answer)
            state["rag_english_query"] = str(english_query)
            state["document_synthesis"] = synthesis_result
            
            # Only increment current_step if called by supervisor (as part of plan)
            if caller == "supervisor":
                state["current_step"] += 1
            
            # Clear query after processing, but keep caller for routing
            state["retriever_query"] = None
            
            print(f"📊 Synthesis completed with confidence: {synthesis_result.get('confidence_assessment', {}).get('overall_confidence', 'N/A')}")
            print(f"🔙 Returning to: {caller}")
            print("✅ === DOCUMENT RETRIEVER AGENT COMPLETED ===\n")
            
            # Set next step for routing and clear caller after processing
            state["next_step"] = None  # Will be determined by conditional edge
            if caller != "supervisor":
                # For non-supervisor callers, we need to return to them
                # The conditional edge will handle the routing
                pass
            
        except ValueError as e:
            print(f"⚠️ No documents found: {e}")
            state["retrieved_documents"] = []
            state["rag_answer"] = ""
            state["document_synthesis"] = {
                "query_analysis": {"original_query": query, "interpreted_intent": ""},
                "synthesis": {"main_findings": "Không tìm thấy tài liệu phù hợp"},
                "confidence_assessment": {"overall_confidence": "low", "reasoning": str(e)},
                "limitations": ["Không có tài liệu trong cơ sở dữ liệu phù hợp với truy vấn"]
            }
            if caller == "supervisor":
                state["current_step"] += 1
            state["retriever_query"] = None
            
        except Exception as e:
            print(f"❌ DocumentRetriever error: {str(e)}")
            state["retrieved_documents"] = []
            state["rag_answer"] = ""
            state["document_synthesis"] = {}
            if caller == "supervisor":
                state["current_step"] += 1
            state["retriever_query"] = None
        return state


def new_document_retriever_node(llm_model=None) -> DocumentRetrieverNode:
    return DocumentRetrieverNode(llm_model=llm_model)
