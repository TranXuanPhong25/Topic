
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Sequence

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore

from .Embedding import (
    DEFAULT_INDEX_NAME,
    connect_vector_store,
    create_embedding_model,
)
from .Reranker import DocumentReranker, create_reranker
from .Router import QueryRouter, QueryType, create_router

load_dotenv()

LOGGER = logging.getLogger(__name__)
DEFAULT_LLM_MODEL = "gemini-2.0-flash"


def _default_query_translator_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """You are a medical terminology expert. Your task is to take a question or symptom description in plain Vietnamese and transform it into a concise, academically rigorous English query suitable for searching medical literature databases.
Based on the symptoms, provide the most likely differential diagnoses.
Combine everything into a single query string.

EXAMPLES:
- Vietnamese question: "da của tôi nổi mẩn đỏ, ngứa và có vảy trắng"
- Academic English query: "Clinical presentation and differential diagnosis for an erythematous, pruritic rash with white scales; consider psoriasis, atopic dermatitis, or tinea corporis."

Vietnamese question: {question}
Academic English query:"""
    )


def _default_final_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """You are a professional AI Medical Research Assistant.

TASK: Analyze the "SOURCE INFORMATION" below to answer the "Original Question" from the user. Your answer must be accurate, concise, and based entirely on provided evidence.

MANDATORY RULES:
1.  **RELY ON CONTEXT ONLY:** Use only information in "SOURCE INFORMATION". Do not infer or use outside knowledge. If you cannot find relevant content in the sources, clearly state no data is available and NEVER create additional information or fake citations.
2.  **SMART CITATION:** Write each paragraph as a complete information block and place at most **one** citation group at the end of that paragraph. If a paragraph is based on multiple sources, combine them in a single pair of brackets as `[Source 1; Source 3]`. Absolutely do not repeat the same source multiple times in the same paragraph. Source indices start from 1.
3.  **ACCURATE REFERENCE LIST:**
    *   At the end of your answer, create a list titled "**References:**".
    *   In this list, **ONLY LIST SOURCES THAT WERE CITED** in the answer.
    *   Each line shows **one source with exactly one page number** (if multiple pages of the same source are needed, repeat the line for each page). Each line must include Author, Title, and specific page number.

NOW, START WITH THE INFORMATION BELOW:
- **Original Question:** {original_question}
- **Academic Query Used:** {english_query}
- **ENGLISH SOURCE INFORMATION FOUND:**
{context}

Analyze and answer in English (following the rules above):"""
    )


def format_context_with_metadata(documents: Sequence[Document]) -> str:
    formatted = []
    for idx, doc in enumerate(documents, start=1):
        metadata = doc.metadata or {}
        title = metadata.get("title", "Không có tiêu đề")
        author = metadata.get("author", "Không có tác giả")
        source_path = metadata.get("source") or metadata.get("file_name") or "Không rõ nguồn"
        source_file = Path(source_path).name
        page_value = metadata.get("page")
        try:
            page_number = int(page_value) + 1 if page_value is not None else "Không rõ"
        except (TypeError, ValueError):
            page_number = metadata.get("page_label", "Không rõ")

        source_info = (
            f"[Nguồn {idx}]:\n"
            f"- Tiêu đề: {title}\n"
            f"- Tác giả: {author}\n"
            f"- Tên file: {source_file}\n"
            f"- Trang: {page_number}"
        )
        formatted.append(f"{source_info}\nNội dung: {doc.page_content}")
    return "\n\n---\n\n".join(formatted)


class RAGPipeline:
    def __init__(
        self,
        *,
        vector_store: PineconeVectorStore,
        llm: ChatGoogleGenerativeAI,
        router: QueryRouter | None = None,
        reranker: DocumentReranker | None = None,
        query_translator_prompt: ChatPromptTemplate | None = None,
        final_prompt: ChatPromptTemplate | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.llm = llm
        self.router = router or create_router(llm)
        self.reranker = reranker or create_reranker()

        translator_prompt = query_translator_prompt or _default_query_translator_prompt()
        answer_prompt = final_prompt or _default_final_prompt()

        self.query_translator_chain = translator_prompt | llm | StrOutputParser()
        self.response_chain = (
            RunnablePassthrough.assign(
                context=lambda inputs: format_context_with_metadata(inputs["context_docs"])
            )
            | answer_prompt
            | llm
            | StrOutputParser()
        )

    def _retrieve_with_routing(
        self,
        query: str,
        query_type: QueryType,
        *,
        k: int,
    ) -> List[Document]:
        if query_type == QueryType.HYBRID:
            search_kwargs = {"k": k * 2}
        else:
            search_kwargs = {"k": k}

        retriever = self.vector_store.as_retriever(search_kwargs=search_kwargs)
        return retriever.invoke(query)

    def invoke(
        self,
        question: str,
        *,
        k: int = 10,
        rerank_top_k: int = 5,
    ) -> Dict[str, object]:
        """
        Run the full RAG flow and return structured results.
        """
        query_type, route_explanation = self.router.route_with_explanation(question)
        english_query = self.query_translator_chain.invoke({"question": question}).strip()

        documents = self._retrieve_with_routing(english_query, query_type, k=k)
        if not documents:
            raise ValueError("No suitable documents found.")

        context_docs = self.reranker.rerank(english_query, documents, top_k=rerank_top_k) or documents
        answer = self.response_chain.invoke(
            {
                "context_docs": context_docs,
                "original_question": question,
                "english_query": english_query,
            }
        )

        return {
            "answer": answer,
            "query_type": query_type,
            "route_explanation": route_explanation,
            "english_query": english_query,
            "context_docs": context_docs,
        }

    @classmethod
    def from_existing_index(
        cls,
        *,
        index_name: str = DEFAULT_INDEX_NAME,
        llm_model: str = DEFAULT_LLM_MODEL,
        temperature: float = 0.3,
    ) -> "RAGPipeline":
        """
        Helper constructor that wires the default embeddings, vector store, and LLM.
        """
        embeddings = create_embedding_model()
        vector_store = connect_vector_store(index_name=index_name, embedding_model=embeddings)
        llm = ChatGoogleGenerativeAI(model=llm_model, temperature=temperature)
        return cls(vector_store=vector_store, llm=llm)


__all__ = [
    "RAGPipeline",
    "format_context_with_metadata",
]