from datetime import datetime, timezone

from schemas.remediation_plan_schema import (
    RemediationItem,
    RemediationSummary,
    RemediationPlan,
)


def build_remediation_plan(run_id: str, gap_result: dict, impact_result: dict) -> RemediationPlan:
    items = []

    gaps = gap_result.get("gaps", [])
    impact_map = {
        item.get("gap_id"): item
        for item in impact_result.get("items", [])
    }

    for gap in gaps:
        gap_id = gap.get("gap_id", "UNKNOWN-GAP")
        impact_data = impact_map.get(gap_id, {})

        priority = impact_data.get("priority", "MEDIUM")
        impact_score = float(impact_data.get("impact_score", 0.0))

        item = RemediationItem(
            gap_id=gap_id,
            requirement_id=gap.get("requirement_id"),
            description=gap.get("description", "Remediate identified gap"),
            owner=gap.get("owner", "Compliance Team"),
            priority=priority,
            due_date=gap.get("due_date"),
            status="PLANNED",
            impact_score=impact_score,
            notes=gap.get("notes"),
        )
        items.append(item)

    owners = {item.owner for item in items}
    high_risk_count = sum(1 for item in items if item.priority == "HIGH")

    summary = RemediationSummary(
        total_gaps=len(items),
        high_risk_gaps=high_risk_count,
        owners_involved=len(owners),
    )

    remediation_plan = RemediationPlan(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        items=items,
    )

    return remediation_plan