
import json
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = Path("data/hr_policy.index")
CHUNKS_PATH = Path("data/chunks.json")


def load_vector_store():
    index = faiss.read_index(str(INDEX_PATH))

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return index, chunks


def retrieve(question, index, chunks, model, top_k=3):
    question_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )

    scores, indices = index.search(question_embedding, top_k)

    results = []

    for score, chunk_index in zip(scores[0], indices[0]):
        if chunk_index == -1:
            continue

        results.append({
            "text": chunks[chunk_index]["text"],
            "page_number": chunks[chunk_index]["page_number"],
            "score": float(score)
        })

    return results


if __name__ == "__main__":
    index, chunks = load_vector_store()
    model = SentenceTransformer(MODEL_NAME)

    question = "How should an employee request annual leave?"
    results = retrieve(question, index, chunks, model)

    print("Question:", question)
    print("Retrieved chunks:", len(results))

    for result in results:
        print("\nPage:", result["page_number"])
        print("Similarity score:", round(result["score"], 4))
        print("Text:", result["text"][:500])
