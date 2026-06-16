from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from schemas.context_packet_schema import (
    ContextPacket,
    DocumentSection,
    EvidencePointer,
)
from utils.pdf_reader import read_pdf_pages


HIGH_RISK_KEYWORDS = ["fine", "penalty", "sanction", "criminal", "breach"]
MEDIUM_RISK_KEYWORDS = ["shall", "must", "required", "compliance"]
LOW_RISK_KEYWORDS = ["may", "guidance", "recommendation"]


def detect_risk_level(text: str) -> str:
    text_lower = text.lower()

    if any(keyword in text_lower for keyword in HIGH_RISK_KEYWORDS):
        return "high"

    if any(keyword in text_lower for keyword in MEDIUM_RISK_KEYWORDS):
        return "medium"

    if any(keyword in text_lower for keyword in LOW_RISK_KEYWORDS):
        return "low"

    return "none"


def determine_filter_status(risk_level: str) -> str:
    if risk_level == "none":
        return "non_regulatory"

    return "relevant"


def detect_source_metadata(text: str) -> tuple[str, str]:
    text_lower = text.lower()

    if "european banking authority" in text_lower or "eba" in text_lower:
        return "European Banking Authority", "European Union"

    if "central bank of kosovo" in text_lower or "bqk" in text_lower:
        return "Central Bank of Kosovo", "Kosovo"

    if "financial conduct authority" in text_lower or "fca" in text_lower:
        return "Financial Conduct Authority", "United Kingdom"

    if (
        "securities and exchange commission" in text_lower
        or "sec" in text_lower
    ):
        return "U.S. Securities and Exchange Commission", "United States"

    return "Unknown", "Unknown"


def build_context_packet(file_path: str) -> ContextPacket:
    path = Path(file_path)
    pages = read_pdf_pages(file_path)

    full_text = " ".join(page["text"] for page in pages)
    source_authority, jurisdiction = detect_source_metadata(full_text)

    sections = []

    for page in pages:
        risk_level = detect_risk_level(page["text"])
        filter_status = determine_filter_status(risk_level)

        section = DocumentSection(
            section_id=f"SEC-{page['page_number']:03}",
            page_number=page["page_number"],
            text=page["text"],
            risk_level=risk_level,
            filter_status=filter_status,
            evidence=EvidencePointer(
                evidence_id=f"EVD-{page['page_number']:03}",
                page_number=page["page_number"],
                bounding_box=page.get("bounding_box")
            )
        )

        sections.append(section)

    context_packet = ContextPacket(
        document_id=f"DOC-{uuid4()}",
        source_file=path.name,
        document_type="pdf",
        document_title=path.stem,
        source_authority=source_authority,
        jurisdiction=jurisdiction,
        document_version="1.0",
        ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
        processing_status="completed",
        total_pages=len(pages),
        sections=sections
    )

    return context_packet