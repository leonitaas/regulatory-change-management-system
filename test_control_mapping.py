import json
from pathlib import Path

from agents.control_mapping_agent import ControlMappingAgent

base = Path(__file__).parent
requirements = json.loads((base / "data/input/requirements.json").read_text(encoding="utf-8"))
controls = json.loads((base / "data/input/controls.json").read_text(encoding="utf-8"))

agent = ControlMappingAgent()
result = agent.generate_control_mapping(requirements=requirements, controls=controls, run_id="RUN-001")

output_path = base / "data/output/control_mapping.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

print(f"Control mapping created successfully: {output_path}")