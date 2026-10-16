
import re
from pdf_reader import extract_pages


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def clean_pages(pages):
    cleaned_pages = []

    for page in pages:
        cleaned_pages.append({
            "page_number": page["page_number"],
            "text": clean_text(page["text"])
        })

    return cleaned_pages


if __name__ == "__main__":
    pages = extract_pages("data/hr_policy.pdf")
    cleaned_pages = clean_pages(pages)

    cleaned_document = "\n".join(
        page["text"] for page in cleaned_pages
    )

    print("Pages processed:", len(cleaned_pages))
    print("Cleaned characters:", len(cleaned_document))
    print("Cleaned text preview:")
    print(cleaned_document[:500])
