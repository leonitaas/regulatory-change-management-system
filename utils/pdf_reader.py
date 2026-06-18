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
        blocks = page.get_text("blocks")

        bounding_box = None

        if blocks:
            x0_values = [block[0] for block in blocks]
            y0_values = [block[1] for block in blocks]
            x1_values = [block[2] for block in blocks]
            y1_values = [block[3] for block in blocks]

            bounding_box = {
                "x0": min(x0_values),
                "y0": min(y0_values),
                "x1": max(x1_values),
                "y1": max(y1_values)
            }

        pages.append({
            "page_number": index,
            "text": text.strip(),
            "bounding_box": bounding_box
        })

    document.close()
    return pages