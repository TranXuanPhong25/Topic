import os
from langchain_community.document_loaders import PyPDFLoader

folder = "data/"

for file in os.listdir(folder):
    if file.lower().endswith(".pdf"):
        path = os.path.join(folder, file)
        print(f"\n===== {file} =====")
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()       # trả về list Document

            if len(docs) > 0:
                meta = docs[0].metadata  # metadata nằm ở từng Document
                if meta:
                    for k, v in meta.items():
                        print(f"{k}: {v}")
                else:
                    print("Không có metadata.")
            else:
                print("Không load được PDF.")

        except Exception as e:
            print("Không đọc được:", e)
