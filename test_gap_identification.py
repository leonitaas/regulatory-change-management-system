import unittest

from agents.agent_gap_identification import identify_gap
from schemas.gap_impact_schema import Policy, Requirement, SystemConfiguration


class GapIdentificationTests(unittest.TestCase):
    def test_returns_no_gap_when_current_policy_covers_requirement(self):
        requirement = Requirement(
            id="REQ-1",
            title="Marketing Disclosures",
            description="Add required performance disclosures.",
            source="Rule",
            category="Marketing",
            effective_date="2026-12-01",
        )
        policies = [
            Policy(
                id="POL-1",
                title="Marketing Policy",
                description="Disclosure standards.",
                last_reviewed="2026-07-01",
                covers_requirements=["REQ-1"],
            )
        ]

        gap = identify_gap(requirement, policies, [])

        self.assertFalse(gap.gap_exists)
        self.assertEqual(gap.gap_type, "none")

    def test_returns_no_gap_when_matching_system_control_exists(self):
        requirement = Requirement(
            id="REQ-2",
            title="T+1 Trade Reporting",
            description="Report trades by T+1.",
            source="Rule",
            category="Trade Reporting",
            effective_date="2026-11-15",
        )
        systems = [
            SystemConfiguration(
                id="SYS-1",
                name="Reporting Gateway",
                description="Regulatory trade reporting workflow.",
                controls=["trade_capture", "regulatory_reporting"],
            )
        ]

        gap = identify_gap(requirement, [], systems)

        self.assertFalse(gap.gap_exists)
        self.assertEqual(gap.gap_type, "none")

    def test_returns_system_gap_when_required_control_is_missing(self):
        requirement = Requirement(
            id="REQ-3",
            title="Enhanced Sanctions Screening",
            description="Screen all payments against sanctions lists.",
            source="Rule",
            category="AML",
            effective_date="2026-09-30",
        )
        systems = [
            SystemConfiguration(
                id="SYS-2",
                name="Client CRM",
                description="Client account system.",
                controls=["account_status_tracking"],
            )
        ]

        gap = identify_gap(requirement, [], systems)

        self.assertTrue(gap.gap_exists)
        self.assertEqual(gap.gap_type, "system_config")


if __name__ == "__main__":
    unittest.main()
