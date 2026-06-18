from datetime import datetime, timezone
from typing import Any, Dict, List

from utils.json_writer import save_json


class ExceptionTriageAgent:
    def __init__(self) -> None:
        pass

    def load_outputs(
        self,
        change_register: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        impact_matrix: Dict[str, Any],
        control_mapping: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "change_register": change_register,
            "gap_analysis": gap_analysis,
            "impact_matrix": impact_matrix,
            "control_mapping": control_mapping,
        }

    def merge_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

       
        change_register = data.get("change_register", {})
        changes = change_register.get("changes", [])

       
        gap_items = data.get("gap_analysis", {}).get("items", [])
        impact_items = data.get("impact_matrix", {}).get("items", [])
        control_items = data.get("control_mapping", {}).get("items", [])

        gaps = {item["requirement_id"]: item for item in gap_items}
        impacts = {item["requirement_id"]: item for item in impact_items}
        controls = {item["requirement_id"]: item for item in control_items}

    
        for idx, change in enumerate(changes):
        
            requirement_id = f"REQ-{idx+1:03d}"

            requirement_text = (
                change.get("requirement_text")
                or ""
            )

            findings.append(
                {
                    "requirement_id": requirement_id,
                    "requirement_text": requirement_text,
                    "jurisdiction": None,  
                    "gap_status": gaps.get(requirement_id, {}).get("gap_status"),
                    "impact_level": impacts.get(requirement_id, {}).get("impact_level"),
                    "mapping_status": controls.get(requirement_id, {}).get("mapping_status"),
                    "owner_suggestion": controls.get(requirement_id, {}).get("owner_suggestion"),
                    "recommended_action": controls.get(requirement_id, {}).get("recommended_control_action"),
                }
            )

        return findings

    def deduplicate_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped: Dict[str, Dict[str, Any]] = {}
        for finding in findings:
            deduped[finding["requirement_id"]] = finding
        return list(deduped.values())

    def categorize_exception(self, finding: Dict[str, Any]) -> str:
        if finding.get("mapping_status") == "missing":
            return "Missing Control"
        if finding.get("mapping_status") == "partial":
            return "Partial Control Coverage"
        if finding.get("gap_status") in ["missing_policy", "outdated_policy"]:
            return "Policy Gap"
        return "Review Required"

    def prioritize_finding(self, finding: Dict[str, Any]) -> str:
        impact = finding.get("impact_level")
        mapping = finding.get("mapping_status")

        if impact == "HIGH" and mapping == "missing":
            return "P1"
        if impact in ["HIGH", "MEDIUM"] and mapping == "partial":
            return "P2"
        return "P3"

    def build_final_report(self, findings: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
        enriched = []

        for finding in findings:
            category = self.categorize_exception(finding)
            priority = self.prioritize_finding(finding)

            enriched.append(
                {
                    **finding,
                    "exception_category": category,
                    "priority": priority,
                    "routing_team": finding.get("owner_suggestion") or "Compliance Team",
                    "decision_reason": f"Assigned {priority} due to impact={finding.get('impact_level')} and mapping={finding.get('mapping_status')}.",
                }
            )

        enriched.sort(key=lambda x: (x["priority"], x["requirement_id"]))

        return {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_findings": len(enriched),
                "p1": sum(1 for x in enriched if x["priority"] == "P1"),
                "p2": sum(1 for x in enriched if x["priority"] == "P2"),
                "p3": sum(1 for x in enriched if x["priority"] == "P3"),
            },
            "items": enriched,
        }

    def build_audit_package(self, report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "run_id": report["run_id"],
            "generated_at": report["generated_at"],
            "audit_trail": [
                {
                    "requirement_id": item["requirement_id"],
                    "priority": item["priority"],
                    "category": item["exception_category"],
                    "decision_reason": item["decision_reason"],
                }
                for item in report["items"]
            ],
        }

    def run(
        self,
        change_register: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        impact_matrix: Dict[str, Any],
        control_mapping: Dict[str, Any],
        run_id: str = "RUN-H-001",
    ) -> Dict[str, Any]:
        data = self.load_outputs(change_register, gap_analysis, impact_matrix, control_mapping)
        findings = self.merge_findings(data)
        findings = self.deduplicate_findings(findings)
        final_report = self.build_final_report(findings, run_id)
        audit_package = self.build_audit_package(final_report)

        save_json(final_report, "data/output/final_report.json")
        save_json(audit_package, "data/output/audit_package.json")

        return final_report