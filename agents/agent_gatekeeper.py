from pathlib import Path

from schemas.context_packet_schema import (
    ContextPacket,
    DocumentSection,
    EvidencePointer,
)
from utils.pdf_reader import read_pdf_pages


def build_context_packet(file_path: str) -> ContextPacket:
    path = Path(file_path)
    pages = read_pdf_pages(file_path)

    sections = []

    for page in pages:
        section = DocumentSection(
            section_id=f"SEC-{page['page_number']:03}",
            page_number=page["page_number"],
            text=page["text"],
            evidence=EvidencePointer(
                page_number=page["page_number"]
            )
        )
        sections.append(section)

    context_packet = ContextPacket(
        source_file=path.name,
        document_type="pdf",
        total_pages=len(pages),
        sections=sections
    )

    return context_packet