from pydantic import BaseModel
from typing import List, Optional


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class ChangeEvidence(BaseModel):
    evidence_id: str
    page_number: int
    section_id: str
    bounding_box: Optional[BoundingBox] = None


class RegulatoryChange(BaseModel):
    change_id: str
    document_id: str
    section_id: str
    requirement_text: str
    requirement_type: str
    confidence_score: float
    validation_status: str
    validation_notes: str
    evidence: ChangeEvidence
    aggregation_group: str


class ChangeRegister(BaseModel):
    document_id: str
    total_changes: int
    changes: List[RegulatoryChange]