from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

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
        document_id=f"DOC-{uuid4()}",
        source_file=path.name,
        document_type="pdf",
        document_title=path.stem,
        ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
        processing_status="completed",
        total_pages=len(pages),
        sections=sections
    )

    return context_packet