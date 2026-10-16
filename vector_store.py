
import json
import faiss
from pathlib import Path
from embeddings import generate_embeddings
from text_chunker import chunk_pages
from pdf_reader import extract_pages
from text_cleaner import clean_pages


DATA_DIR = Path("data")
INDEX_PATH = DATA_DIR / "hr_policy.index"
CHUNKS_PATH = DATA_DIR / "chunks.json"


def build_vector_store(chunks):
    embeddings = generate_embeddings(chunks)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    return index


if __name__ == "__main__":
    pages = extract_pages("data/hr_policy.pdf")
    cleaned_pages = clean_pages(pages)
    chunks = chunk_pages(cleaned_pages)

    index = build_vector_store(chunks)

    print("Total chunks indexed:", index.ntotal)
    print("Vector dimensions:", index.d)
    print("Index saved:", INDEX_PATH)
    print("Chunks saved:", CHUNKS_PATH)
