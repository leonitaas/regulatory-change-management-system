from agents.agent_gatekeeper import build_context_packet
from utils.json_writer import save_json


def main():
    input_file = "data/input/regulation.pdf"
    output_file = "data/output/context_packet.json"

    context_packet = build_context_packet(input_file)

    save_json(
        context_packet.model_dump(),
        output_file
    )

    print(f"Context packet created successfully: {output_file}")


if __name__ == "__main__":
    main()