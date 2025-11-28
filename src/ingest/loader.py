import os

def load_documents(data_path="data"):
    documents = []

    for file in os.listdir(data_path):
        if file.endswith(".md") or file.endswith(".txt"):
            file_path = os.path.join(data_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                documents.append({
                    "filename": file,
                    "content": f.read()
                })
    
    print(f"[Loader] {len(documents)} documents loaded.")
    return documents
