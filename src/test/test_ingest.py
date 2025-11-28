from src.ingest.loader import load_documents
from src.ingest.chunker import chunk_text

docs = load_documents("data")

for doc in docs:
    chunks = chunk_text(doc["content"])
    print(doc["filename"], "=>", len(chunks), "chunks")

