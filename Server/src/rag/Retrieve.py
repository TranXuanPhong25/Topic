# import os
# from dotenv import load_dotenv
# from pinecone import Pinecone
# from langchain_pinecone import PineconeVectorStore
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser

# # ==============================================================================
# # BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG VÀ CÁC CÔNG CỤ
# # ==============================================================================

# load_dotenv()
# print("Khởi tạo công cụ embedding 'models/text-embedding-004'...")
# embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
# print("Khởi tạo LLM 'gemini-2.0-flash'...")
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# # ==============================================================================
# # BƯỚC 2: KẾT NỐI VỚI PINECONE VÀ TẠO RETRIEVER CƠ BẢN
# # ==============================================================================

# index_name = "rag-on-pinecone"
# print(f"Kết nối tới index '{index_name}' trên Pinecone...")
# try:
#     docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
#     print("Kết nối thành công!")
# except Exception as e:
#     print(f"Kết nối thất bại: {e}")
#     exit()

# # Tạo retriever cơ bản, sẽ được sử dụng sau khi câu hỏi được biến đổi
# base_retriever = docsearch.as_retriever(search_kwargs={'k': 7})

# # ==============================================================================
# # CẢI TIẾN CỐT LÕI: XÂY DỰNG CHUỖI BIẾN ĐỔI CÂU HỎI
# # ==============================================================================
# print("Xây dựng chuỗi biến đổi câu hỏi (Query Transformation)...")

# # Prompt này có nhiệm vụ dịch và làm giàu câu hỏi
# query_translator_prompt = ChatPromptTemplate.from_template(
# """Bạn là một chuyên gia thuật ngữ y khoa. Nhiệm vụ của bạn là nhận một câu hỏi hoặc mô tả triệu chứng bằng tiếng Việt thông thường và biến đổi nó thành một câu truy vấn bằng tiếng Anh học thuật, súc tích, phù hợp để tìm kiếm trong cơ sở dữ liệu y văn.
# Dựa trên các triệu chứng, hãy đưa ra các chẩn đoán phân biệt (differential diagnoses) có khả năng nhất.
# Hãy kết hợp tất cả thành một chuỗi truy vấn duy nhất.

# VÍ DỤ:
# - Câu hỏi tiếng Việt: "da của tôi nổi mẩn đỏ, ngứa và có vảy trắng"
# - Câu truy vấn tiếng Anh học thuật: "Clinical presentation and differential diagnosis for an erythematous, pruritic rash with white scales; consider psoriasis, atopic dermatitis, or tinea corporis."

# Câu hỏi tiếng Việt: {question}
# Câu truy vấn tiếng Anh học thuật:"""
# )

# # Chuỗi này chỉ làm một nhiệm vụ: Dịch và làm giàu câu hỏi
# query_translator_chain = query_translator_prompt | llm | StrOutputParser()

# # ==============================================================================
# # BƯỚC 3: XÂY DỰNG CHUỖI TẠO CÂU TRẢ LỜI CUỐI CÙNG
# # ==============================================================================
# print("Xây dựng chuỗi RAG cuối cùng...")

# def dinh_dang_ngu_canh_chi_tiet(docs):
#     # ... (Hàm này giữ nguyên như phiên bản trước) ...
#     formatted_docs = []
#     for i, doc in enumerate(docs):
#         metadata = doc.metadata
#         title = metadata.get('title', 'Không có tiêu đề')
#         author = metadata.get('author', 'Không có tác giả')
#         source_file = os.path.basename(metadata.get('source', 'Không rõ nguồn file'))
#         page_num = int(metadata.get('page', -1) + 1)
#         source_info = (f"[Nguồn {i+1}]:\n- Tiêu đề: {title}\n- Tác giả: {author}\n- Tên file: {source_file}\n- Trang: {page_num}")
#         content = f"Nội dung: {doc.page_content}"
#         formatted_docs.append(f"{source_info}\n{content}")
#     return "\n\n---\n\n".join(formatted_docs)

# # Prompt mới này sẽ nhận ngữ cảnh tiếng Anh nhưng trả lời câu hỏi tiếng Việt
# final_rag_prompt = ChatPromptTemplate.from_template(
# """Bạn là một Trợ lý Nghiên cứu Y khoa AI.

# NHIỆM VỤ: Trả lời **câu hỏi gốc bằng tiếng Việt** của người dùng, dựa DUY NHẤT vào các **nguồn thông tin học thuật bằng tiếng Anh** được cung cấp. Câu trả lời cuối cùng của bạn **BẮT BUỘC phải bằng tiếng Việt**.

# QUY TẮC:
# 1.  **DỰA VÀO NGỮ CẢNH:** Chỉ sử dụng thông tin trong mục "NGUỒN THÔNG TIN TIẾNG ANH".
# 2.  **TRÍCH DẪN:** Với mỗi mệnh đề, phải kết thúc bằng trích dẫn `[Nguồn X]`.
# 3.  **DANH SÁCH THAM KHẢO:** Cuối câu trả lời, tạo danh sách "Nguồn tham khảo:" chi tiết.
# 4.  **XỬ LÝ THÔNG TIN KHÔNG ĐẦY ĐỦ:** Nếu các nguồn không chứa thông tin liên quan, hãy trả lời bằng tiếng Việt: "Dựa trên các tài liệu được cung cấp, tôi không tìm thấy thông tin để trả lời câu hỏi này."

# NGUỒN THÔNG TIN TIẾNG ANH:
# ---
# {context}
# ---

# Câu hỏi gốc bằng tiếng Việt: {original_question}
# Phân tích và trả lời bằng tiếng Việt (tuân thủ nghiêm ngặt các quy tắc trên):"""
# )

# # Chuỗi này giờ nhận ngữ cảnh đã được xử lý và câu hỏi gốc để tạo câu trả lời
# rag_chain = (
#     RunnablePassthrough.assign(context=lambda inputs: dinh_dang_ngu_canh_chi_tiet(inputs['context_docs']))
#     | final_rag_prompt
#     | llm
#     | StrOutputParser()
# )

# print("\nHệ thống đã sẵn sàng. Bạn có thể bắt đầu đặt câu hỏi.")
# print("----------------------------------------------------")

# # Vòng lặp chính đã được viết lại hoàn toàn
# while True:
#     original_question = input("Câu hỏi của bạn (gõ 'exit' để thoát): ")
#     if original_question.lower() == 'exit':
#         break
    
#     # BƯỚC A: BIẾN ĐỔI CÂU HỎI GỐC
#     print("\n--- Đang dịch và làm giàu câu hỏi ---")
#     english_query = query_translator_chain.invoke({"question": original_question})
#     print(f"Câu truy vấn tiếng Anh học thuật: {english_query}")
#     print("------------------------------------")

#     # BƯỚC B: TRUY XUẤT TÀI LIỆU
#     print("--- Đang truy xuất tài liệu liên quan ---")
#     retrieved_docs = base_retriever.invoke(english_query)
#     print(f"Đã tìm thấy {len(retrieved_docs)} tài liệu liên quan.")
#     print("--------------------------------------")
    
#     if not retrieved_docs:
#         print("\n--- Phản hồi ---")
#         print("Dựa trên các tài liệu được cung cấp, tôi không tìm thấy thông tin để trả lời câu hỏi này.")
#         print("---------------\n")
#         continue

#     # BƯỚC C: TẠO CÂU TRẢ LỜI CUỐI CÙNG
#     response = rag_chain.invoke({
#         "context_docs": retrieved_docs,
#         "original_question": original_question
#     })
    
#     print("\n--- Phản hồi học thuật ---")
#     print(response)
#     print("--------------------------\n")

# ... (Tất cả code từ BƯỚC 1 và BƯỚC 2 giữ nguyên) ...
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
print("Khởi tạo công cụ embedding 'models/text-embedding-004'...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
print("Khởi tạo LLM 'gemini-2.0-flash'...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

index_name = "rag-on-pinecone"
print(f"Kết nối tới index '{index_name}' trên Pinecone...")
try:
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
    print("Kết nối thành công!")
except Exception as e:
    print(f"Kết nối thất bại: {e}")
    exit()

base_retriever = docsearch.as_retriever(search_kwargs={'k': 7})

print("Xây dựng chuỗi biến đổi câu hỏi (Query Transformation)...")
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
# BƯỚC 3: XÂY DỰNG CHUỖI TẠO CÂU TRẢ LỜI CUỐI CÙNG (ĐÃ SỬA LỖI)
# ==============================================================================
print("Xây dựng chuỗi RAG cuối cùng...")

def dinh_dang_ngu_canh_chi_tiet(docs):
    # ... (Hàm này giữ nguyên) ...
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

# SỬA LỖI 1: Nâng cấp prompt cuối cùng để nhận thêm thông tin
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

print("\nHệ thống đã sẵn sàng. Bạn có thể bắt đầu đặt câu hỏi.")
print("----------------------------------------------------")

while True:
    original_question = input("Câu hỏi của bạn (gõ 'exit' để thoát): ")
    if original_question.lower() == 'exit':
        break
    
    print("\n--- Đang dịch và làm giàu câu hỏi ---")
    english_query = query_translator_chain.invoke({"question": original_question})
    print(f"Câu truy vấn tiếng Anh học thuật: {english_query}")
    print("------------------------------------")

    print("--- Đang truy xuất tài liệu liên quan ---")
    retrieved_docs = base_retriever.invoke(english_query)
    print(f"Đã tìm thấy {len(retrieved_docs)} tài liệu liên quan.")
    for doc in retrieved_docs:
        print(f"- Tiêu đề: {doc.page_content}...")  # In một phần nội dung để nhận biết
    print("--------------------------------------")
    
    if not retrieved_docs:
        print("\n--- Phản hồi ---")
        print("Dựa trên các tài liệu được cung cấp, tôi không tìm thấy thông tin để trả lời câu hỏi này.")
        print("---------------\n")
        continue

    # SỬA LỖI 2: Truyền cả `english_query` vào chuỗi cuối cùng
    response = rag_chain.invoke({
        "context_docs": retrieved_docs,
        "original_question": original_question,
        "english_query": english_query  # <-- Thêm thông tin này
    })
    
    print("\n--- Phản hồi học thuật ---")
    print(response)
    print("--------------------------\n")