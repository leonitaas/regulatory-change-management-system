from schemas.context_packet_schema import ContextPacket
from schemas.change_register_schema import (
    ChangeRegister,
    RegulatoryChange,
    ChangeEvidence,
)


def extract_changes(context_packet: ContextPacket) -> ChangeRegister:
    changes = []

    for index, section in enumerate(context_packet.sections, start=1):
        if not section.text.strip():
            continue

        change = RegulatoryChange(
            change_id=f"CHG-{index:03}",
            document_id=context_packet.document_id,
            section_id=section.section_id,
            requirement_text=section.text,
            requirement_type="obligation",
            confidence_score=1.0,
            evidence=ChangeEvidence(
                page_number=section.page_number,
                section_id=section.section_id
            )
        )

        changes.append(change)

    return ChangeRegister(
        document_id=context_packet.document_id,
        total_changes=len(changes),
        changes=changes
    )