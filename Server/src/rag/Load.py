import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Tải các biến môi trường từ file .env
load_dotenv()

# --- PHẦN CODE ĐƯỢC THAY ĐỔI ---

# 1. Tải tất cả tài liệu từ một thư mục
data_folder = "data/"
all_documents = []

# Duyệt qua tất cả các file trong thư mục data
for filename in os.listdir(data_folder):
    file_path = os.path.join(data_folder, filename)

    # Kiểm tra phần mở rộng của file để chọn loader phù hợp
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        print(f"Đang tải file PDF: {filename}")
        all_documents.extend(loader.load())
    elif filename.endswith(".txt"):
        loader = TextLoader(file_path, encoding='utf-8') # Thêm encoding để hỗ trợ tiếng Việt
        print(f"Đang tải file TXT: {filename}")
        all_documents.extend(loader.load())
    # Bạn có thể thêm các loại file khác ở đây (ví dụ: .docx, .csv)
    # elif filename.endswith(".docx"):
    #     loader = Docx2txtLoader(file_path)
    #     all_documents.extend(loader.load())
    else:
        print(f"Bỏ qua file không hỗ trợ: {filename}")

print(f"\nĐã tải thành công {len(all_documents)} trang/tài liệu từ thư mục '{data_folder}'.")

# 2. Chia tất cả tài liệu đã tải thành các đoạn nhỏ (chunks)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(all_documents)

print(f"Tổng số đoạn văn bản được tạo ra: {len(docs)}")
if docs:
    print(f"Nội dung đoạn đầu tiên: {docs[0].page_content}")

# --- KẾT THÚC PHẦN THAY ĐỔI ---