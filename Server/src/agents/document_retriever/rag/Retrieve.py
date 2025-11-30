"""Composable RAG pipeline that can be imported as a module."""

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
        """Bạn là một chuyên gia thuật ngữ y khoa. Nhiệm vụ của bạn là nhận một câu hỏi hoặc mô tả triệu chứng bằng tiếng Việt thông thường và biến đổi nó thành một câu truy vấn bằng tiếng Anh học thuật, súc tích, phù hợp để tìm kiếm trong cơ sở dữ liệu y văn.
Dựa trên các triệu chứng, hãy đưa ra các chẩn đoán phân biệt (differential diagnoses) có khả năng nhất.
Hãy kết hợp tất cả thành một chuỗi truy vấn duy nhất.

VÍ DỤ:
- Câu hỏi tiếng Việt: "da của tôi nổi mẩn đỏ, ngứa và có vảy trắng"
- Câu truy vấn tiếng Anh học thuật: "Clinical presentation and differential diagnosis for an erythematous, pruritic rash with white scales; consider psoriasis, atopic dermatitis, or tinea corporis."

Câu hỏi tiếng Việt: {question}
Câu truy vấn tiếng Anh học thuật:"""
    )


def _default_final_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """Bạn là một Trợ lý Nghiên cứu Y khoa AI chuyên nghiệp.

NHIỆM VỤ: Phân tích các "NGUỒN THÔNG TIN" dưới đây để trả lời "Câu hỏi gốc bằng tiếng Việt" của người dùng. Câu trả lời của bạn phải chính xác, súc tích và hoàn toàn dựa trên bằng chứng được cung cấp.

QUY TẮC BẮT BUỘC:
1.  **DỰA VÀO NGỮ CẢNH:** Chỉ sử dụng thông tin trong "NGUỒN THÔNG TIN". Không suy diễn hay dùng kiến thức ngoài. Nếu không tìm thấy nội dung phù hợp trong nguồn, hãy trả lời rõ ràng rằng không có dữ liệu và KHÔNG tạo thêm thông tin hay trích dẫn giả.
2.  **TRÍCH DẪN THÔNG MINH:** Viết mỗi đoạn như một khối thông tin hoàn chỉnh và chỉ đặt tối đa **một** cụm trích dẫn ở cuối đoạn đó. Nếu đoạn dựa trên nhiều nguồn, gộp chúng trong một cặp ngoặc duy nhất theo dạng `[Nguồn 1; Nguồn 3]`. Tuyệt đối không lặp lại cùng nguồn nhiều lần trong cùng đoạn. Các chỉ số nguồn bắt đầu từ 1.
3.  **DANH SÁCH THAM KHẢO CHÍNH XÁC:**
    *   Ở cuối câu trả lời, tạo một danh sách có tiêu đề "**Tài liệu tham khảo:**".
    *   Trong danh sách này, **CHỈ LIỆT KÊ NHỮNG NGUỒN ĐÃ ĐƯỢC TRÍCH DẪN** trong câu trả lời.
    *   Mỗi dòng chỉ trình bày **một nguồn với đúng một số trang** (nếu cần nhiều trang của cùng nguồn thì lặp lại dòng đó cho từng trang). Mỗi dòng phải gồm Tác giả, Tiêu đề, và Số trang cụ thể.

BÂY GIỜ, HÃY BẮT ĐẦU VỚI CÁC THÔNG TIN DƯỚI ĐÂY:
- **Câu hỏi gốc bằng tiếng Việt:** {original_question}
- **Câu truy vấn học thuật đã dùng:** {english_query}
- **NGUỒN THÔNG TIN TIẾNG ANH TÌM ĐƯỢC:**
{context}

Phân tích và trả lời bằng tiếng Việt (tuân thủ các quy tắc nêu trên):"""
    )


def format_context_with_metadata(documents: Sequence[Document]) -> str:
    """Format retrieved documents so the generator can cite them."""
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
    """High-level facade that wires routing, reranking, and response generation."""

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
            raise ValueError("Không tìm thấy tài liệu phù hợp.")

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