from datetime import datetime, timezone

from schemas.remediation_plan_schema import (
    RemediationItem,
    RemediationSummary,
    RemediationPlan,
)


def build_remediation_plan(run_id: str, gap_result: dict, impact_result: dict) -> RemediationPlan:
    items = []

    for gap in gap_result.get("gaps", []):
        item = RemediationItem(
            gap_id=gap["gap_id"],
            requirement_id=gap.get("requirement_id"),
            description=gap.get("description", "Remediate identified gap"),
            owner="Compliance Team",
            priority="HIGH",
            due_date=None,
            status="PLANNED",
            impact_score=0.0,
            notes=None
        )
        items.append(item)

    summary = RemediationSummary(
        total_gaps=len(items),
        high_risk_gaps=sum(1 for item in items if item.priority == "HIGH"),
        owners_involved=1
    )

    remediation_plan = RemediationPlan(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        items=items
    )

    return remediation_plan