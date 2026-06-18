import json
from datetime import date, timedelta
from pathlib import Path

from agents.agent_gatekeeper import build_context_packet
from agents.agent_change_extraction import extract_changes
from agents.agent_impact_assessment import run_gap_impact_analysis

from schemas.change_register_schema import ChangeRegister
from schemas.context_packet_schema import ContextPacket
from schemas.gap_impact_schema import Policy, Requirement, SystemConfiguration
from utils.json_writer import save_json


def main():
    input_file = "data/input/regulation.pdf"

    context_packet = build_context_packet(input_file)

    save_json(
        context_packet.model_dump(),
        "data/output/context_packet.json"
    )

    change_register = extract_changes(context_packet)

    save_json(
        change_register.model_dump(),
        "data/output/change_register.json"
    )

    requirements = load_requirements(change_register, context_packet)
    policies = load_policies()
    systems = load_systems()

    gap_impact_result = run_gap_impact_analysis(
        requirements,
        policies,
        systems,
    )

    save_json(
        gap_impact_result.model_dump(),
        "data/output/gap_impact_result.json"
    )

    print("IRCMS pipeline executed successfully.")
    print("Generated:")
    print("- data/output/context_packet.json")
    print("- data/output/change_register.json")
    print("- data/output/gap_impact_result.json")
    print()
    print_gap_impact_report(gap_impact_result)


def load_requirements(
    change_register: ChangeRegister,
    context_packet: ContextPacket,
) -> list[Requirement]:
    if change_register.changes:
        default_effective = (date.today() + timedelta(days=180)).isoformat()

        return [
            Requirement(
                id=change.change_id,
                title=f"{change.requirement_type.replace('_', ' ').title()} requirement",
                description=change.requirement_text,
                source=context_packet.source_authority,
                category=change.requirement_type,
                effective_date=default_effective,
            )
            for change in change_register.changes
        ]

    return load_json_models("data/input/requirements.json", Requirement)


def load_policies() -> list[Policy]:
    return load_json_models("data/input/policies.json", Policy)


def load_systems() -> list[SystemConfiguration]:
    return load_json_models("data/input/systems.json", SystemConfiguration)


def load_json_models(file_path: str, model):
    path = Path(file_path)
    records = json.loads(path.read_text(encoding="utf-8"))
    return [model(**record) for record in records]


def print_gap_impact_report(result):
    summary = result.summary
    line = "=" * 72

    print(line)
    print("  GAP ANALYSIS & IMPACT ASSESSMENT REPORT")
    print(line)

    print("\nSUMMARY")
    print("-" * 72)
    print(f"  Requirements analysed:  {summary.total_requirements}")
    print(f"  Gaps identified:        {summary.gaps_identified}")
    print(f"  Impacts assessed:       {summary.impacts_assessed}")
    print(f"  Integrity check:        {'PASS' if summary.integrity_passed else 'FAIL'}")
    print(f"  Remediation items:      {summary.remediation_items}")

    print("\nGAPS")
    print("-" * 72)
    for gap in result.gaps:
        status = "GAP" if gap.gap_exists else "OK "
        print(
            f"  {status}  {gap.requirement_id:<12} "
            f"sev={gap.severity:<8} type={gap.gap_type:<14} "
            f"conf={gap.confidence:.2f}"
        )
        print(f"        {gap.gap_summary}")

    print("\nIMPACTS")
    print("-" * 72)
    for impact in result.impacts:
        print(
            f"  {impact.requirement_id:<12} "
            f"risk={impact.compliance_risk_score}/10  "
            f"complexity={impact.remediation_complexity_score}/10  "
            f"headcount={impact.headcount_affected}"
        )
        print(f"        units:     {', '.join(impact.impacted_business_units)}")
        print(f"        systems:   {', '.join(impact.impacted_systems)}")
        print(f"        processes: {', '.join(impact.impacted_processes)}")

    print("\nREMEDIATION PLAN")
    print("-" * 72)
    if not result.remediation_plan:
        print("  (not generated - resolve integrity errors first)")
    else:
        for rank, item in enumerate(result.remediation_plan, start=1):
            due = (
                f"due in {item.days_until_due}d"
                if item.days_until_due >= 0
                else f"OVERDUE {abs(item.days_until_due)}d"
            )
            print(
                f"  #{rank}  P={item.priority_score:<5}  {item.requirement_id:<12} "
                f"{due:<14} owner={item.suggested_owner}"
            )
            print(f"        {item.title}")
    print()


if __name__ == "__main__":
    main()
