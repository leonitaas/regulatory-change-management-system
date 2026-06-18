import json
from agents.exception_triage import ExceptionTriageAgent

with open("data/output/change_register.json", "r", encoding="utf-8") as f:
    change_register = json.load(f)

with open("data/output/control_mapping.json", "r", encoding="utf-8") as f:
    control_mapping = json.load(f)

with open("data/output/gap_analysis.json", "r", encoding="utf-8") as f:
    gap_analysis = json.load(f)

with open("data/output/impact_matrix.json", "r", encoding="utf-8") as f:
    impact_matrix = json.load(f)

agent = ExceptionTriageAgent()
result = agent.run(
    change_register=change_register,
    gap_analysis=gap_analysis,
    impact_matrix=impact_matrix,
    control_mapping=control_mapping,
    run_id="RUN-H-TEST-001",
)

print("Agent H test completed.")
print("Total findings:", result["summary"]["total_findings"])
print("change_register keys:", change_register.keys())
print("control_mapping keys:", control_mapping.keys())
print("gap_analysis keys:", gap_analysis.keys())
print("impact_matrix keys:", impact_matrix.keys())
