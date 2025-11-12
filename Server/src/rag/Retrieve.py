import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ==============================================================================
# BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG VÀ CÁC CÔNG CỤ
# ==============================================================================

# Tải các biến môi trường
load_dotenv()

# Khởi tạo lại công cụ embedding (PHẢI CÙNG MODEL VỚI FILE EMBEDDING)
print("Khởi tạo công cụ embedding...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Khởi tạo LLM của Google theo yêu cầu
print("Khởi tạo LLM (gemini-2.0-flash)...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)

# ==============================================================================
# BƯỚC 2: KẾT NỐI LẠI VỚI PINECONE INDEX ĐÃ TỒN TẠI
# ==============================================================================

index_name = "rag-on-pinecone"
print(f"Kết nối tới index '{index_name}' trên Pinecone...")

try:
    # Tải lại vector store đã có từ Pinecone
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
    print("Kết nối thành công!")
except Exception as e:
    print(f"Kết nối thất bại: {e}")
    exit()

# Tạo retriever từ vector store
retriever = docsearch.as_retriever(search_kwargs={'k': 5})

# ==============================================================================
# BƯỚC 3: XÂY DỰNG CHUỖI RAG VỚI TRÍCH DẪN NGUỒN CHI TIẾT
# ==============================================================================
print("Xây dựng chuỗi RAG với khả năng trích dẫn nguồn chi tiết...")

# THAY ĐỔI 1: Nâng cấp hàm định dạng ngữ cảnh để lấy thêm metadata
def format_docs_with_rich_sources(docs):
    """
    Định dạng các tài liệu truy xuất để bao gồm thông tin metadata chi tiết.
    Cung cấp cho LLM một cấu trúc rõ ràng để nó có thể trích dẫn đầy đủ.
    """
    formatted_docs = []
    for i, doc in enumerate(docs):
        # Trích xuất thông tin từ metadata, có giá trị mặc định nếu thiếu
        metadata = doc.metadata
        title = metadata.get('title', 'Tiêu đề không xác định')
        author = metadata.get('author', 'Tác giả không xác định')
        source_file = os.path.basename(metadata.get('source', 'Nguồn không xác định'))
        page_num = metadata.get('page', -1) + 1

        # Tạo một khối thông tin có cấu trúc cho mỗi nguồn
        source_info = (
            f"Source [{i+1}]:\n"
            f"- Source: {title}\n"
            f"- Author: {author}\n"
            f"- Page: {int(page_num)}"
        )
        content = f"Content: {doc.page_content}"
        
        formatted_docs.append(f"{source_info}\n{content}")
        
    return "\n\n---\n\n".join(formatted_docs)


# THAY ĐỔI 2: Nâng cấp Prompt để yêu cầu LLM sử dụng metadata chi tiết
prompt_template = """
Bạn là một trợ lý AI chuyên nghiệp, có nhiệm vụ trả lời câu hỏi của người dùng dựa DUY NHẤT vào các nguồn thông tin chi tiết được cung cấp dưới đây.

QUY TẮC BẮT BUỘC:
1.  Phân tích kỹ thông tin từ các nguồn trước khi trả lời.
2.  Khi bạn sử dụng thông tin từ một nguồn để trả lời, bạn PHẢI trích dẫn nguồn đó bằng cách thêm `[Source X]` vào cuối câu, trong đó X là số của nguồn.
3.  Nếu một câu được tổng hợp từ nhiều nguồn, hãy trích dẫn tất cả các nguồn, ví dụ: `[Source 1, Source 3]`.
4.  Ở cuối câu trả lời, hãy tạo một danh sách tham khảo chi tiết dưới tiêu đề "Nguồn tham khảo:". Với mỗi nguồn đã sử dụng, hãy liệt kê đầy đủ thông tin: Tiêu đề, Tác giả, Tên file, và Số trang.
5.  Nếu không có nguồn nào chứa thông tin để trả lời câu hỏi, hãy trả lời: "Tôi không tìm thấy thông tin liên quan trong các tài liệu được cung cấp."

NGUỒN THÔNG TIN CHI TIẾT:
---
{context}
---

Câu hỏi của người dùng: {question}

Câu trả lời của bạn (hãy tuân thủ nghiêm ngặt các quy tắc trên):
"""
prompt = ChatPromptTemplate.from_template(prompt_template)


# THAY ĐỔI 3: Cập nhật chuỗi RAG để sử dụng hàm định dạng mới
rag_chain = (
    {"context": retriever | format_docs_with_rich_sources, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("\nHệ thống đã sẵn sàng. Bạn có thể bắt đầu đặt câu hỏi.")
print("----------------------------------------------------")

# Vòng lặp để hỏi đáp liên tục
while True:
    question = input("Câu hỏi của bạn (gõ 'exit' để thoát): ")
    if question.lower() == 'exit':
        break
    
    response = rag_chain.invoke(question)
    
    print("\n--- Câu trả lời ---")
    print(response)
    print("-------------------\n")