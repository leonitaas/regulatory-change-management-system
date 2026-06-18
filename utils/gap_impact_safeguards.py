from schemas.gap_impact_schema import (
    GapAnalysis,
    ImpactAssessment,
    IntegrityIssue,
    Requirement,
)

LOW_CONFIDENCE_THRESHOLD = 0.5


def validate_gap_impact_outputs(
    requirements: list[Requirement],
    gaps: list[GapAnalysis],
    impacts: list[ImpactAssessment],
) -> list[IntegrityIssue]:
    issues = []
    requirement_ids = {requirement.id for requirement in requirements}
    gap_by_requirement = {gap.requirement_id: gap for gap in gaps}
    impact_by_requirement = {
        impact.requirement_id: impact for impact in impacts
    }

    for gap in gaps:
        if gap.requirement_id not in requirement_ids:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=gap.requirement_id,
                    message="Gap references an unknown requirement.",
                )
            )

    for impact in impacts:
        if impact.requirement_id not in requirement_ids:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=impact.requirement_id,
                    message="Impact references an unknown requirement.",
                )
            )

    for requirement in requirements:
        if requirement.id not in gap_by_requirement:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=requirement.id,
                    message="Requirement was never analysed by gap identification.",
                )
            )

    for gap in gaps:
        if gap.gap_exists and gap.requirement_id not in impact_by_requirement:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=gap.requirement_id,
                    message="Confirmed gap has no impact assessment.",
                )
            )

    for impact in impacts:
        gap = gap_by_requirement.get(impact.requirement_id)
        if gap is None or not gap.gap_exists:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=impact.requirement_id,
                    message="Impact assessment exists with no confirmed gap.",
                )
            )

    for impact in impacts:
        if not 1 <= impact.compliance_risk_score <= 10:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=impact.requirement_id,
                    message=(
                        f"compliance_risk_score {impact.compliance_risk_score} "
                        "out of range (1-10)."
                    ),
                )
            )

        if not 1 <= impact.remediation_complexity_score <= 10:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=impact.requirement_id,
                    message=(
                        f"remediation_complexity_score "
                        f"{impact.remediation_complexity_score} out of range (1-10)."
                    ),
                )
            )

        if impact.headcount_affected < 0:
            issues.append(
                IntegrityIssue(
                    severity="error",
                    requirement_id=impact.requirement_id,
                    message="headcount_affected is negative.",
                )
            )

    for gap in gaps:
        if gap.gap_exists and gap.confidence < LOW_CONFIDENCE_THRESHOLD:
            issues.append(
                IntegrityIssue(
                    severity="warning",
                    requirement_id=gap.requirement_id,
                    message=(
                        f"Low-confidence gap ({gap.confidence:.2f}) "
                        "requires manual review."
                    ),
                )
            )

    return issues
