from pathlib import Path
import fitz


def read_pdf_pages(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported at this stage.")

    document = fitz.open(str(path))
    pages = []

    for index, page in enumerate(document, start=1):
        text = page.get_text("text") or ""

        pages.append({
            "page_number": index,
            "text": text.strip()
        })

    document.close()
    return pages