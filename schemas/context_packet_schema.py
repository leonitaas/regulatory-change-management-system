from pydantic import BaseModel
from typing import List


class EvidencePointer(BaseModel):
    page_number: int


class DocumentSection(BaseModel):
    section_id: str
    page_number: int
    text: str
    evidence: EvidencePointer


class ContextPacket(BaseModel):
    source_file: str
    document_type: str
    total_pages: int
    sections: List[DocumentSection]