
from sentence_transformers import SentenceTransformer
from text_chunker import chunk_pages
from pdf_reader import extract_pages
from text_cleaner import clean_pages


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def generate_embeddings(chunks):
    if not chunks:
        raise ValueError("No text chunks available")

    model = SentenceTransformer(MODEL_NAME)
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings


if __name__ == "__main__":
    pages = extract_pages("data/hr_policy.pdf")
    cleaned_pages = clean_pages(pages)
    chunks = chunk_pages(cleaned_pages)
    embeddings = generate_embeddings(chunks)

    print("Total PDF pages:", len(pages))
    print("Total chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)
    print("First vector preview:", embeddings[0][:10])

