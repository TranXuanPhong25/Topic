import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Import routing and reranking modules
from Router import QueryRouter, QueryType, create_router
from Reranker import DocumentReranker, create_reranker

# ==============================================================================
# BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG VÀ CÁC CÔNG CỤ
# ==============================================================================

load_dotenv()
print("🔧 Khởi tạo công cụ embedding 'models/text-embedding-004'...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
print("🔧 Khởi tạo LLM 'gemini-2.0-flash'...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# ==============================================================================
# BƯỚC 2: KẾT NỐI VỚI PINECONE VÀ TẠO RETRIEVER CƠ BẢN
# ==============================================================================

index_name = "rag-on-pinecone"
print(f"🔌 Kết nối tới index '{index_name}' trên Pinecone...")
try:
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
    print("✓ Kết nối thành công!")
except Exception as e:
    print(f"❌ Kết nối thất bại: {e}")
    exit()

# ==============================================================================
# BƯỚC 3: KHỞI TẠO ROUTER VÀ RERANKER
# ==============================================================================

print("🚦 Khởi tạo Query Router...")
router = create_router(llm)

print("📊 Khởi tạo Document Reranker...")
reranker = create_reranker()

# ==============================================================================
# BƯỚC 4: XÂY DỰNG CHUỖI BIẾN ĐỔI CÂU HỎI
# ==============================================================================
print("🔄 Xây dựng chuỗi biến đổi câu hỏi (Query Transformation)...")

query_translator_prompt = ChatPromptTemplate.from_template(
"""Bạn là một chuyên gia thuật ngữ y khoa. Nhiệm vụ của bạn là nhận một câu hỏi hoặc mô tả triệu chứng bằng tiếng Việt thông thường và biến đổi nó thành một câu truy vấn bằng tiếng Anh học thuật, súc tích, phù hợp để tìm kiếm trong cơ sở dữ liệu y văn.
Dựa trên các triệu chứng, hãy đưa ra các chẩn đoán phân biệt (differential diagnoses) có khả năng nhất.
Hãy kết hợp tất cả thành một chuỗi truy vấn duy nhất.

VÍ DỤ:
- Câu hỏi tiếng Việt: "da của tôi nổi mẩn đỏ, ngứa và có vảy trắng"
- Câu truy vấn tiếng Anh học thuật: "Clinical presentation and differential diagnosis for an erythematous, pruritic rash with white scales; consider psoriasis, atopic dermatitis, or tinea corporis."

Câu hỏi tiếng Việt: {question}
Câu truy vấn tiếng Anh học thuật:"""
)
query_translator_chain = query_translator_prompt | llm | StrOutputParser()

# ==============================================================================
# BƯỚC 5: HÀM TRUY XUẤT VỚI ROUTING
# ==============================================================================

def retrieve_with_routing(query: str, query_type: QueryType, k: int = 10):
    """
    Retrieve documents using the appropriate strategy based on query type.
    
    Args:
        query: The search query
        query_type: Type of query (semantic, keyword, hybrid)
        k: Number of documents to retrieve
        
    Returns:
        List of retrieved documents
    """
    if query_type == QueryType.SEMANTIC:
        # Pure semantic/vector search
        retriever = docsearch.as_retriever(search_kwargs={'k': k})
        docs = retriever.invoke(query)
        
    elif query_type == QueryType.KEYWORD:
        # Keyword-based search (if Pinecone supports it, otherwise use semantic)
        # For now, use semantic with higher k and filter later
        retriever = docsearch.as_retriever(search_kwargs={'k': k})
        docs = retriever.invoke(query)
        
    elif query_type == QueryType.HYBRID:
        # Hybrid: retrieve more docs and rely on reranker
        retriever = docsearch.as_retriever(search_kwargs={'k': k * 2})
        docs = retriever.invoke(query)
    else:
        # Default to semantic
        retriever = docsearch.as_retriever(search_kwargs={'k': k})
        docs = retriever.invoke(query)
    
    return docs

# ==============================================================================
# BƯỚC 6: XÂY DỰNG CHUỖI TẠO CÂU TRẢ LỜI CUỐI CÙNG
# ==============================================================================
print("🔗 Xây dựng chuỗi RAG cuối cùng...")

def dinh_dang_ngu_canh_chi_tiet(docs):
    """Format documents with detailed metadata for context"""
    formatted_docs = []
    for i, doc in enumerate(docs):
        metadata = doc.metadata
        title = metadata.get('title', 'Không có tiêu đề')
        author = metadata.get('author', 'Không có tác giả')
        source_file = os.path.basename(metadata.get('source', 'Không rõ nguồn file'))
        page_num = int(metadata.get('page', -1) + 1)
        source_info = (f"[Nguồn {i+1}]:\n- Tiêu đề: {title}\n- Tác giả: {author}\n- Tên file: {source_file}\n- Trang: {page_num}")
        content = f"Nội dung: {doc.page_content}"
        formatted_docs.append(f"{source_info}\n{content}")
    return "\n\n---\n\n".join(formatted_docs)

final_rag_prompt = ChatPromptTemplate.from_template(
"""Bạn là một Trợ lý Nghiên cứu Y khoa AI chuyên nghiệp.

NHIỆM VỤ: Phân tích các "NGUỒN THÔNG TIN" dưới đây để trả lời "Câu hỏi gốc bằng tiếng Việt" của người dùng. Câu trả lời của bạn phải chính xác, súc tích và hoàn toàn dựa trên bằng chứng được cung cấp.

QUY TẮC BẮT BUỘC:
1.  **DỰA VÀO NGỮ CẢNH:** Chỉ sử dụng thông tin trong "NGUỒN THÔNG TIN". Không suy diễn hay dùng kiến thức ngoài.
2.  **TRÍCH DẪN THÔNG MINH:** Chỉ trích dẫn `[Nguồn X]` ở cuối đoạn trực tiếp rút ra thông tin từ nguồn đó. TRÁNH trích dẫn không cần thiết hoặc lặp lại ở mọi câu. các trích dẫn được đánh bắt đầu từ 1.
3.  **DANH SÁCH THAM KHẢO CHÍNH XÁC:**
    *   Ở cuối câu trả lời, tạo một danh sách có tiêu đề "**Tài liệu tham khảo:**".
    *   Trong danh sách này, **CHỈ LIỆT KÊ NHỮNG NGUỒN MÀ BẠN ĐÃ THỰC SỰ TRÍCH DẪN** trong câu trả lời.
    *   Mỗi nguồn phải được trình bày trên một dòng riêng, bao gồm **ĐẦY ĐỦ** thông tin: Tác giả, Tiêu đề, và **SỐ TRANG** cụ thể.

VÍ DỤ VỀ ĐỊNH DẠNG ĐẦU RA MONG MUỐN:
---
**Phản hồi học thuật**
Herpes zoster, còn gọi là zona, là tình trạng đau dây thần kinh và phát ban da nghiêm trọng do nhiễm virus ở hạch thần kinh cảm giác hoặc hạch dây thần kinh sọ não [Nguồn 2]. Tình trạng này xảy ra khi một hạch thần kinh bị ảnh hưởng [Nguồn 1]. Đau do herpes zoster gây ra được đề cập đến trong bối cảnh các loại đau khác nhau, bao gồm cả đau đầu [Nguồn 5].

**Tài liệu tham khảo:**
*   [Nguồn 1] Hall, John E. Phd. *Pocket Companion to Guyton & Hall Textbook of Medical Physiology*. Trang: 389.
*   [Nguồn 2] Hall, John E. Phd. *Pocket Companion to Guyton & Hall Textbook of Medical Physiology*. Trang: 457.
*   [Nguồn 5] Hall, John E. Phd. *Pocket Companion to Guyton & Hall Textbook of Medical Physiology*. Trang: 584.
---

BÂY GIỜ, HÃY BẮT ĐẦU VỚI CÁC THÔNG TIN DƯỚI ĐÂY:
- **Câu hỏi gốc bằng tiếng Việt:** {original_question}
- **Câu truy vấn học thuật đã dùng:** {english_query}
- **NGUỒN THÔNG TIN TIẾNG ANH TÌM ĐƯỢC:**
{context}

Phân tích và trả lời bằng tiếng Việt (tuân thủ nghiêm ngặt các quy tắc và định dạng ví dụ trên):"""
)

rag_chain = (
    RunnablePassthrough.assign(context=lambda inputs: dinh_dang_ngu_canh_chi_tiet(inputs['context_docs']))
    | final_rag_prompt
    | llm
    | StrOutputParser()
)

# ==============================================================================
# BƯỚC 7: VÒNG LẶP CHÍNH VỚI ROUTING VÀ RERANKING
# ==============================================================================

print("\n✅ Hệ thống đã sẵn sàng với Routing và Reranking!")
print("="*70)

while True:
    original_question = input("\n💬 Câu hỏi của bạn (gõ 'exit' để thoát): ")
    if original_question.lower() == 'exit':
        break
    
    print("\n" + "="*70)
    
    # BƯỚC A: ROUTING - Phân loại câu hỏi
    print("🚦 [ROUTING] Đang phân tích loại câu hỏi...")
    query_type, route_explanation = router.route_with_explanation(original_question)
    print(f"   → {route_explanation}")
    
    # BƯỚC B: QUERY TRANSFORMATION - Dịch và làm giàu câu hỏi
    print("\n🔄 [QUERY TRANSFORMATION] Đang dịch và làm giàu câu hỏi...")
    english_query = query_translator_chain.invoke({"question": original_question})
    print(f"   → Câu truy vấn: {english_query}")
    
    # BƯỚC C: RETRIEVAL - Truy xuất tài liệu theo strategy
    print(f"\n🔍 [RETRIEVAL] Đang truy xuất tài liệu (strategy: {query_type.value})...")
    retrieved_docs = retrieve_with_routing(english_query, query_type, k=10)
    print(f"   → Đã tìm thấy {len(retrieved_docs)} tài liệu ban đầu")
    
    if not retrieved_docs:
        print("\n" + "="*70)
        print("❌ Không tìm thấy tài liệu liên quan.")
        print("="*70)
        continue
    
    # BƯỚC D: RERANKING - Sắp xếp lại theo độ liên quan
    print("\n📊 [RERANKING] Đang sắp xếp lại tài liệu theo độ liên quan...")
    reranked_docs = reranker.rerank(english_query, retrieved_docs, top_k=5)
    print(f"   → Chọn top {len(reranked_docs)} tài liệu có độ liên quan cao nhất")
    
    # BƯỚC E: GENERATION - Tạo câu trả lời cuối cùng
    print("\n💡 [GENERATION] Đang tạo câu trả lời...")
    response = rag_chain.invoke({
        "context_docs": reranked_docs,
        "original_question": original_question,
        "english_query": english_query
    })
    
    print("\n" + "="*70)
    print("📝 PHẢN HỒI HỌC THUẬT")
    print("="*70)
    print(response)
    print("="*70)