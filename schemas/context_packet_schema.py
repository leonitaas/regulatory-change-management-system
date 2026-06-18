
from pydantic import BaseModel
from typing import List, Optional


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class EvidencePointer(BaseModel):
    evidence_id: str
    page_number: int
    bounding_box: Optional[BoundingBox] = None


class DocumentSection(BaseModel):
    section_id: str
    page_number: int
    text: str
    risk_level: str
    filter_status: str
    evidence: EvidencePointer
    
    


class ContextPacket(BaseModel):
    document_id: str
    source_file: str
    document_type: str
    jurisdiction: str
    source_authority: str
    document_version: str
    document_title: Optional[str] = None
    ingestion_timestamp: str
    processing_status: str
    total_pages: int
    sections: List[DocumentSection]