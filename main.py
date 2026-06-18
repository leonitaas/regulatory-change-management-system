from agents.agent_gatekeeper import build_context_packet
from agents.agent_change_extraction import extract_changes
from agents.agent_change_extraction import extract_changes_with_llm

from utils.json_writer import save_json


def main():
    input_file = "data/input/regulation.pdf"

    context_packet = build_context_packet(input_file)

    save_json(
        context_packet.model_dump(),
        "data/output/context_packet.json"
    )

    change_register = extract_changes_with_llm(context_packet)

    save_json(
        change_register.model_dump(),
        "data/output/change_register.json"
    )

    print("IRCMS pipeline executed successfully.")
    print("Generated:")
    print("- context_packet.json")
    print("- change_register.json")


if __name__ == "__main__":
    main()