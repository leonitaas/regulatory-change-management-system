from pydantic import BaseModel
from typing import List


class ChangeEvidence(BaseModel):
    page_number: int
    section_id: str


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


class ChangeRegister(BaseModel):
    document_id: str
    total_changes: int
    changes: List[RegulatoryChange]