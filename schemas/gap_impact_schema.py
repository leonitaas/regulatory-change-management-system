from typing import List, Optional

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str
    title: str
    description: str
    source: str
    category: str
    effective_date: str


class Policy(BaseModel):
    id: str
    title: str
    description: str
    last_reviewed: str
    covers_requirements: List[str] = Field(default_factory=list)


class SystemConfiguration(BaseModel):
    id: str
    name: str
    description: str
    controls: List[str] = Field(default_factory=list)


class GapAnalysis(BaseModel):
    requirement_id: str
    gap_exists: bool
    gap_type: str
    current_state: str
    required_state: str
    gap_summary: str
    severity: str
    confidence: float


class ImpactAssessment(BaseModel):
    requirement_id: str
    impacted_processes: List[str]
    impacted_systems: List[str]
    impacted_business_units: List[str]
    headcount_affected: int
    compliance_risk_score: int
    remediation_complexity_score: int
    rationale: str


class IntegrityIssue(BaseModel):
    severity: str
    requirement_id: str
    message: str


class RemediationItem(BaseModel):
    requirement_id: str
    title: str
    gap_summary: str
    severity: str
    compliance_risk_score: int
    remediation_complexity_score: int
    priority_score: float
    days_until_due: int
    impacted_business_units: List[str]
    suggested_owner: str


class GapImpactSummary(BaseModel):
    total_requirements: int
    gaps_identified: int
    impacts_assessed: int
    integrity_passed: bool
    remediation_items: int


class GapImpactResult(BaseModel):
    summary: GapImpactSummary
    gaps: List[GapAnalysis]
    impacts: List[ImpactAssessment]
    integrity_issues: List[IntegrityIssue]
    remediation_plan: List[RemediationItem]
