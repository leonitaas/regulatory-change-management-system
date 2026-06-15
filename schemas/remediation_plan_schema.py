from pydantic import BaseModel
from typing import List, Optional


class RemediationItem(BaseModel):
    gap_id: str
    requirement_id: Optional[str] = None
    description: str
    owner: str
    priority: str
    due_date: Optional[str] = None
    status: str
    impact_score: float
    notes: Optional[str] = None


class RemediationSummary(BaseModel):
    total_gaps: int
    high_risk_gaps: int
    owners_involved: int


class RemediationPlan(BaseModel):
    run_id: str
    generated_at: str
    summary: RemediationSummary
    items: List[RemediationItem]