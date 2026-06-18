from datetime import date

from schemas.gap_impact_schema import (
    GapAnalysis,
    GapImpactResult,
    GapImpactSummary,
    ImpactAssessment,
    Policy,
    RemediationItem,
    Requirement,
    SystemConfiguration,
)
from agents.agent_gap_identification import identify_gap
from utils.gap_impact_safeguards import validate_gap_impact_outputs


SEVERITY_RISK_SCORES = {
    "low": 3,
    "medium": 5,
    "high": 7,
    "critical": 9,
}

GAP_TYPE_COMPLEXITY_SCORES = {
    "none": 2,
    "policy": 3,
    "procedure": 5,
    "system_config": 8,
}

SEVERITY_PRIORITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

DOMAIN_IMPACT_MAP = {
    "aml": {
        "processes": ["Transaction monitoring", "Customer due diligence"],
        "systems": ["AML Monitoring Platform", "Client CRM"],
        "units": ["Compliance", "Operations"],
        "headcount": 24,
    },
    "data privacy": {
        "processes": ["Data retention", "Account closure"],
        "systems": ["Client CRM", "Data Warehouse"],
        "units": ["Compliance", "IT", "Client Success"],
        "headcount": 16,
    },
    "marketing": {
        "processes": ["Material review and approval"],
        "systems": ["Marketing Asset Library"],
        "units": ["Marketing", "Compliance"],
        "headcount": 9,
    },
    "best execution": {
        "processes": ["Order routing", "Execution-quality review"],
        "systems": ["Order Management System"],
        "units": ["Trading", "Compliance"],
        "headcount": 12,
    },
    "trade reporting": {
        "processes": ["Trade capture", "Regulatory reporting"],
        "systems": ["Order Management System", "Reporting Gateway"],
        "units": ["Operations", "Compliance"],
        "headcount": 14,
    },
}

DEFAULT_DOMAIN_IMPACT = {
    "processes": ["Compliance review"],
    "systems": ["Client CRM"],
    "units": ["Compliance"],
    "headcount": 6,
}


def assess_impact(requirement: Requirement, gap: GapAnalysis) -> ImpactAssessment:
    domain = DOMAIN_IMPACT_MAP.get(
        requirement.category.strip().lower(),
        DEFAULT_DOMAIN_IMPACT,
    )

    return ImpactAssessment(
        requirement_id=requirement.id,
        impacted_processes=list(domain["processes"]),
        impacted_systems=list(domain["systems"]),
        impacted_business_units=list(domain["units"]),
        headcount_affected=domain["headcount"],
        compliance_risk_score=SEVERITY_RISK_SCORES[gap.severity],
        remediation_complexity_score=GAP_TYPE_COMPLEXITY_SCORES[gap.gap_type],
        rationale=(
            f"{requirement.category} change of {gap.severity} severity "
            f"requiring {gap.gap_type.replace('_', ' ')} remediation across "
            f"{len(domain['units'])} business unit(s)."
        ),
    )


def run_gap_impact_analysis(
    requirements: list[Requirement],
    policies: list[Policy],
    systems: list[SystemConfiguration],
    *,
    today: date | None = None,
) -> GapImpactResult:
    today = today or date.today()

    gaps = []
    impacts = []

    for requirement in requirements:
        gap = identify_gap(requirement, policies, systems)
        gaps.append(gap)

        if gap.gap_exists:
            impacts.append(assess_impact(requirement, gap))

    integrity_issues = validate_gap_impact_outputs(requirements, gaps, impacts)
    integrity_passed = not any(
        issue.severity == "error" for issue in integrity_issues
    )

    remediation_plan = []
    if integrity_passed:
        remediation_plan = _build_remediation_plan(
            requirements,
            gaps,
            impacts,
            today,
        )

    gaps_identified = sum(1 for gap in gaps if gap.gap_exists)

    return GapImpactResult(
        summary=GapImpactSummary(
            total_requirements=len(requirements),
            gaps_identified=gaps_identified,
            impacts_assessed=len(impacts),
            integrity_passed=integrity_passed,
            remediation_items=len(remediation_plan),
        ),
        gaps=gaps,
        impacts=impacts,
        integrity_issues=integrity_issues,
        remediation_plan=remediation_plan,
    )


def _build_remediation_plan(
    requirements: list[Requirement],
    gaps: list[GapAnalysis],
    impacts: list[ImpactAssessment],
    today: date,
) -> list[RemediationItem]:
    requirement_by_id = {requirement.id: requirement for requirement in requirements}
    gap_by_id = {gap.requirement_id: gap for gap in gaps}

    items = []
    for impact in impacts:
        requirement = requirement_by_id[impact.requirement_id]
        gap = gap_by_id[impact.requirement_id]
        days_until_due = (
            date.fromisoformat(requirement.effective_date) - today
        ).days

        items.append(
            RemediationItem(
                requirement_id=requirement.id,
                title=requirement.title,
                gap_summary=gap.gap_summary,
                severity=gap.severity,
                compliance_risk_score=impact.compliance_risk_score,
                remediation_complexity_score=impact.remediation_complexity_score,
                priority_score=_calculate_priority_score(
                    gap,
                    impact,
                    days_until_due,
                ),
                days_until_due=days_until_due,
                impacted_business_units=list(impact.impacted_business_units),
                suggested_owner=(
                    impact.impacted_business_units[0]
                    if impact.impacted_business_units
                    else "Compliance"
                ),
            )
        )

    items.sort(key=lambda item: item.priority_score, reverse=True)
    return items


def _calculate_priority_score(
    gap: GapAnalysis,
    impact: ImpactAssessment,
    days_until_due: int,
) -> float:
    risk = impact.compliance_risk_score / 10.0
    severity = SEVERITY_PRIORITY_WEIGHT[gap.severity] / 4.0

    if days_until_due <= 0:
        urgency = 1.0
    elif days_until_due <= 30:
        urgency = 0.9
    elif days_until_due <= 90:
        urgency = 0.6
    elif days_until_due <= 180:
        urgency = 0.4
    else:
        urgency = 0.2

    return round(100 * (0.45 * risk + 0.25 * severity + 0.30 * urgency), 1)
