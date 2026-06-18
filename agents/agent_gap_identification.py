from datetime import date, timedelta

from schemas.gap_impact_schema import (
    GapAnalysis,
    Policy,
    Requirement,
    SystemConfiguration,
)


STALE_POLICY_DAYS = 548

HIGH_SEVERITY_KEYWORDS = ["aml", "anti-money", "sanction", "fraud"]
MEDIUM_SEVERITY_KEYWORDS = ["privacy", "data retention", "best execution"]
CONTROL_MATCH_KEYWORDS = {
    "aml": ["sanction", "monitoring", "screening", "counterparty"],
    "data privacy": ["data", "retention", "account", "closure", "anonymise"],
    "marketing": ["marketing", "performance", "disclosure", "advertising"],
    "best execution": ["execution", "venue", "routing", "order"],
    "trade reporting": ["trade", "reporting", "regulatory", "capture"],
}


def identify_gap(
    requirement: Requirement,
    policies: list[Policy],
    systems: list[SystemConfiguration],
) -> GapAnalysis:
    covering = [
        policy for policy in policies
        if requirement.id in policy.covers_requirements
    ]
    current = [
        policy for policy in covering
        if _is_policy_current(policy, requirement)
    ]
    matching_systems = [
        system for system in systems
        if _system_matches_requirement(system, requirement)
    ]

    if current or matching_systems:
        current_state = _build_current_state(current, matching_systems)
        return GapAnalysis(
            requirement_id=requirement.id,
            gap_exists=False,
            gap_type="none",
            current_state=current_state,
            required_state=requirement.description,
            gap_summary="Existing policy or system controls already cover this requirement.",
            severity="low",
            confidence=0.7,
        )

    if covering:
        gap_type = "policy"
        current_state = (
            f"{covering[0].title} last reviewed {covering[0].last_reviewed}, "
            "predating the new requirement and not yet updated for it."
        )
    elif _requires_system_control(requirement):
        gap_type = "system_config"
        current_state = "No system control currently enforces this requirement."
    else:
        gap_type = "procedure"
        current_state = "No documented procedure addresses this requirement."

    return GapAnalysis(
        requirement_id=requirement.id,
        gap_exists=True,
        gap_type=gap_type,
        current_state=current_state,
        required_state=requirement.description,
        gap_summary=f"Firm does not yet satisfy '{requirement.title}'.",
        severity=_determine_severity(requirement),
        confidence=0.6,
    )


def _is_policy_current(policy: Policy, requirement: Requirement) -> bool:
    effective = date.fromisoformat(requirement.effective_date)
    reviewed = date.fromisoformat(policy.last_reviewed)
    return reviewed >= effective - timedelta(days=STALE_POLICY_DAYS)


def _build_current_state(
    current_policies: list[Policy],
    matching_systems: list[SystemConfiguration],
) -> str:
    parts = []

    if current_policies:
        parts.append(
            f"Addressed by {current_policies[0].title} "
            f"(reviewed {current_policies[0].last_reviewed})."
        )

    if matching_systems:
        parts.append(
            "Supported by system controls in "
            f"{matching_systems[0].name}."
        )

    return " ".join(parts)


def _system_matches_requirement(
    system: SystemConfiguration,
    requirement: Requirement,
) -> bool:
    keywords = CONTROL_MATCH_KEYWORDS.get(requirement.category.lower(), [])
    searchable_text = " ".join(
        [system.name, system.description, *system.controls]
    ).lower()

    if not keywords:
        return False

    return any(keyword in searchable_text for keyword in keywords)


def _requires_system_control(requirement: Requirement) -> bool:
    return requirement.category.lower() in {"aml", "data privacy", "trade reporting"}


def _determine_severity(requirement: Requirement) -> str:
    text = (
        f"{requirement.title} {requirement.description} "
        f"{requirement.category}"
    ).lower()

    if any(keyword in text for keyword in HIGH_SEVERITY_KEYWORDS):
        return "critical"

    if any(keyword in text for keyword in MEDIUM_SEVERITY_KEYWORDS):
        return "high"

    return "medium"
