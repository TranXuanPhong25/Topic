from Load import load_and_chunk_documents
from Embedding import index_documents

def main():
    docs = load_and_chunk_documents()      # đọc + clean + chunk từ rag/Data
    index_documents(docs)                  # đảm bảo index và push lên Pinecone
    print(f"Indexed {len(docs)} chunks.")

if __name__ == "__main__":
    main()