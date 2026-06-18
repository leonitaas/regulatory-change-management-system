from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, List

from schemas.control_mapping_schema import (
    ControlMappingItem,
    ControlMappingResult,
    ControlMappingSummary,
    EvidenceRequirement,
    MappedControl,
)


class ControlMappingAgent:
    def __init__(self, full_threshold: float = 0.55, partial_threshold: float = 0.3):
        self.full_threshold = full_threshold
        self.partial_threshold = partial_threshold

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().replace("_", " ").replace("-", " ").split())

    def _token_overlap(self, a: str, b: str) -> float:
        a_tokens = set(self._normalize(a).split())
        b_tokens = set(self._normalize(b).split())
        if not a_tokens or not b_tokens:
            return 0.0
        return len(a_tokens & b_tokens) / len(a_tokens)

    def _similarity(self, requirement_text: str, control: Dict[str, Any]) -> float:
        control_text = f"{control.get('control_name', '')} {control.get('description', '')}"
        ratio = SequenceMatcher(None, self._normalize(requirement_text), self._normalize(control_text)).ratio()
        overlap = self._token_overlap(requirement_text, control_text)
        return round((ratio * 0.45) + (overlap * 0.55), 2)

    def _owner_suggestion(self, requirement_text: str) -> str:
        text = self._normalize(requirement_text)
        if any(k in text for k in ["access", "security", "privileged"]):
            return "Security Team"
        if any(k in text for k in ["policy", "governance", "compliance"]):
            return "Compliance Team"
        if any(k in text for k in ["vendor", "third party", "supplier"]):
            return "Risk Team"
        return "Control Owner Team"

    def _estimated_effort(self, status: str) -> str:
        if status == "mapped":
            return "LOW"
        if status == "partial":
            return "MEDIUM"
        return "HIGH"

    def _recommended_action(self, status: str) -> str:
        if status == "mapped":
            return "Validate evidence and confirm existing control coverage."
        if status == "partial":
            return "Enhance existing control or update policy to close the coverage gap."
        return "Design and implement a new control to satisfy the requirement."

    def _evidence_requirements(self, requirement_text: str, status: str) -> List[EvidenceRequirement]:
        base = [
            EvidenceRequirement(
                evidence_type="Control Documentation",
                description="Documented control description, owner, and execution frequency.",
            ),
            EvidenceRequirement(
                evidence_type="Implementation Evidence",
                description="Artifacts proving the control is implemented and operational.",
            ),
        ]

        text = self._normalize(requirement_text)

        if "policy" in text:
            base.append(
                EvidenceRequirement(
                    evidence_type="Policy Document",
                    description="Latest approved policy version with review date.",
                )
            )

        if any(k in text for k in ["access", "privileged"]):
            base.append(
                EvidenceRequirement(
                    evidence_type="Access Review Records",
                    description="Logs or review sign-offs for privileged access checks.",
                )
            )

        if any(k in text for k in ["vendor", "third party"]):
            base.append(
                EvidenceRequirement(
                    evidence_type="Vendor Assessment",
                    description="Due diligence and risk assessment records for third parties.",
                )
            )

        if status == "missing":
            base.append(
                EvidenceRequirement(
                    evidence_type="Remediation Plan",
                    description="Planned actions, timeline, and assigned owner for new control implementation.",
                )
            )

        return base

    def _overlap_notes(self, requirement: Dict[str, Any], matched_controls: List[MappedControl]) -> str | None:
        jurisdictions = requirement.get("applicable_jurisdictions", [])
        if len(jurisdictions) > 1:
            return f"Requirement spans multiple jurisdictions: {', '.join(jurisdictions)}. Validate overlap with shared controls."
        if matched_controls and len({c.jurisdiction for c in matched_controls if c.jurisdiction}) > 1:
            return "Matched controls come from multiple jurisdictions; confirm harmonized control coverage."
        return None

    def _conflict_notes(self, requirement: Dict[str, Any], matched_controls: List[MappedControl]) -> str | None:
        if requirement.get("conflicting_standard"):
            return f"Potential conflict noted with standard: {requirement['conflicting_standard']}. Review control design for consistency."
        if matched_controls and any(c.match_type == "partial" for c in matched_controls):
            return "Partial matches may indicate inconsistent control language or differing control standards."
        return None

    def generate_control_mapping(
        self,
        requirements: List[Dict[str, Any]],
        controls: List[Dict[str, Any]],
        run_id: str = "RUN-001",
    ) -> ControlMappingResult:
        items: List[ControlMappingItem] = []
        full = partial = unmapped = new_controls_required = 0

        for req in requirements:
            scored_matches = []
            for ctrl in controls:
                score = self._similarity(req.get("requirement_text", ""), ctrl)
                if score >= self.partial_threshold:
                    scored_matches.append((score, ctrl))

            scored_matches.sort(key=lambda x: x[0], reverse=True)
            top_matches = scored_matches[:3]

            mapped_controls: List[MappedControl] = []
            for score, ctrl in top_matches:
                match_type = "full" if score >= self.full_threshold else "partial"
                mapped_controls.append(
                    MappedControl(
                        control_id=ctrl.get("control_id", "UNKNOWN"),
                        control_name=ctrl.get("control_name", "Unnamed Control"),
                        jurisdiction=ctrl.get("jurisdiction"),
                        match_type=match_type,
                        coverage_score=score,
                        notes=ctrl.get("description"),
                    )
                )

            if mapped_controls and mapped_controls[0].coverage_score >= self.full_threshold:
                mapping_status = "mapped"
                new_control_required = False
                gap_reason = None
                full += 1
            elif mapped_controls:
                mapping_status = "partial"
                new_control_required = False
                gap_reason = "Existing controls provide only partial coverage for this requirement."
                partial += 1
            else:
                mapping_status = "missing"
                new_control_required = True
                gap_reason = "No existing control sufficiently maps to this requirement."
                unmapped += 1
                new_controls_required += 1

            owner = self._owner_suggestion(req.get("requirement_text", ""))
            effort = self._estimated_effort(mapping_status)
            action = self._recommended_action(mapping_status)
            evidence = self._evidence_requirements(req.get("requirement_text", ""), mapping_status)
            overlap_notes = self._overlap_notes(req, mapped_controls)
            conflict_notes = self._conflict_notes(req, mapped_controls)

            items.append(
                ControlMappingItem(
                    requirement_id=req.get("requirement_id", "UNKNOWN"),
                    requirement_text=req.get("requirement_text", ""),
                    jurisdiction=req.get("jurisdiction"),
                    matched_controls=mapped_controls,
                    mapping_status=mapping_status,
                    new_control_required=new_control_required,
                    recommended_control_action=action,
                    owner_suggestion=owner,
                    estimated_effort=effort,
                    evidence_requirements=evidence,
                    overlap_notes=overlap_notes,
                    conflict_notes=conflict_notes,
                    gap_reason=gap_reason,
                )
            )

        summary = ControlMappingSummary(
            total_requirements=len(requirements),
            fully_mapped=full,
            partially_mapped=partial,
            unmapped=unmapped,
            new_controls_required=new_controls_required,
        )

        return ControlMappingResult(
            run_id=run_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            items=items,
        )