from typing import List, Optional
from pydantic import BaseModel


class MappedControl(BaseModel):
    control_id: str
    control_name: str
    jurisdiction: Optional[str] = None
    match_type: str
    coverage_score: float
    notes: Optional[str] = None


class EvidenceRequirement(BaseModel):
    evidence_type: str
    description: str


class ControlMappingItem(BaseModel):
    requirement_id: str
    requirement_text: str
    jurisdiction: Optional[str] = None
    matched_controls: List[MappedControl]
    mapping_status: str
    new_control_required: bool
    recommended_control_action: str
    owner_suggestion: str
    estimated_effort: str
    evidence_requirements: List[EvidenceRequirement]
    overlap_notes: Optional[str] = None
    conflict_notes: Optional[str] = None
    gap_reason: Optional[str] = None


class ControlMappingSummary(BaseModel):
    total_requirements: int
    fully_mapped: int
    partially_mapped: int
    unmapped: int
    new_controls_required: int


class ControlMappingResult(BaseModel):
    run_id: str
    generated_at: str
    summary: ControlMappingSummary
    items: List[ControlMappingItem]