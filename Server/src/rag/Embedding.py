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
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Khởi tạo embedding model của Google
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Khởi tạo Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Đặt tên cho index của bạn
index_name = "rag-on-pinecone"

# Kiểm tra xem index đã tồn tại chưa, nếu chưa thì tạo mới
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Kích thước của embedding model "models/text-embedding-004"
        metric="cosine", # Sử dụng độ đo cosine để tính sự tương đồng
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Đã tạo index '{index_name}'")
else:
    print(f"Index '{index_name}' đã tồn tại.")

# Tải các đoạn văn bản và embedding của chúng lên Pinecone
# Đây là bước lập chỉ mục (indexing)
docsearch = PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)

print("Đã tải thành công các embeddings lên Pinecone.")