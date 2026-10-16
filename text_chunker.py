
from pdf_reader import extract_pages
from text_cleaner import clean_pages


def chunk_pages(pages, chunk_size=500, overlap=50):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    for page in pages:
        text = page["text"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "page_number": page["page_number"]
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks


if __name__ == "__main__":
    pages = extract_pages("data/hr_policy.pdf")
    cleaned_pages = clean_pages(pages)
    chunks = chunk_pages(cleaned_pages)

    print("Total PDF pages:", len(pages))
    print("Total chunks:", len(chunks))

    if chunks:
        print("First chunk:")
        print(chunks[0]["text"])
        print("First chunk page:", chunks[0]["page_number"])
