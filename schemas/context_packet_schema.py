
from pydantic import BaseModel
from typing import List, Optional


class EvidencePointer(BaseModel):
    page_number: int


class DocumentSection(BaseModel):
    section_id: str
    page_number: int
    text: str
    evidence: EvidencePointer


class ContextPacket(BaseModel):
    document_id: str
    source_file: str
    document_type: str
    document_title: Optional[str] = None
    ingestion_timestamp: str
    processing_status: str
    total_pages: int
    sections: List[DocumentSection]