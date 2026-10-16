
from pypdf import PdfReader


def extract_pages(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    return pages


if __name__ == "__main__":
    pages = extract_pages("hr_policy.pdf")

    print("Total pages:", len(pages))
    print("First page preview:")
    print(pages[0]["text"][:300] if pages else "PDF has no pages")

