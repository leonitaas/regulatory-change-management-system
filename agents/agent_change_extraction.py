import re

from schemas.context_packet_schema import ContextPacket
from schemas.change_register_schema import (
    ChangeRegister,
    RegulatoryChange,
    ChangeEvidence,
)


OBLIGATION_KEYWORDS = [
    "shall",
    "must",
    "required to",
    "is required to",
    "are required to",
]

PROHIBITION_KEYWORDS = [
    "shall not",
    "must not",
    "prohibited",
    "may not",
]

PERMISSION_KEYWORDS = [
    "may",
    "permitted",
    "allowed",
]

TIMELINE_KEYWORDS = [
    "effective date",
    "effective from",
    "by no later than",
    "within",
]

AMBIGUOUS_KEYWORDS = [
    "where appropriate",
    "as applicable",
    "reasonable",
    "may be required",
    "subject to",
    "if necessary",
]


def normalize_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    normalized_text = normalize_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", normalized_text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def classify_requirement_type(sentence: str) -> str | None:
    sentence_lower = sentence.lower()

    if any(keyword in sentence_lower for keyword in PROHIBITION_KEYWORDS):
        return "prohibition"

    if any(keyword in sentence_lower for keyword in OBLIGATION_KEYWORDS):
        return "obligation"

    if any(keyword in sentence_lower for keyword in TIMELINE_KEYWORDS):
        return "timeline"

    if any(keyword in sentence_lower for keyword in PERMISSION_KEYWORDS):
        return "permission"

    return None


def calculate_confidence_score(requirement_type: str, sentence: str) -> float:
    sentence_lower = sentence.lower()

    if any(keyword in sentence_lower for keyword in AMBIGUOUS_KEYWORDS):
        return 0.65

    if requirement_type == "obligation" and (
        "shall" in sentence_lower or "must" in sentence_lower
    ):
        return 0.95

    if requirement_type == "prohibition" and (
        "shall not" in sentence_lower or "must not" in sentence_lower
    ):
        return 0.95

    if requirement_type == "timeline" and (
        "effective from" in sentence_lower or "effective date" in sentence_lower
    ):
        return 0.90

    if requirement_type == "permission" and "may" in sentence_lower:
        return 0.85

    return 0.80


def validate_requirement(confidence_score: float, sentence: str) -> tuple[str, str]:
    sentence_lower = sentence.lower()

    if any(keyword in sentence_lower for keyword in AMBIGUOUS_KEYWORDS):
        return (
            "requires_review",
            "Ambiguous regulatory language detected."
        )

    if confidence_score >= 0.85:
        return (
            "auto_accepted",
            "Requirement passed rule-based validation."
        )

    return (
        "requires_review",
        "Low confidence extraction requires manual review."
    )


def extract_changes(context_packet: ContextPacket) -> ChangeRegister:
    changes = []
    change_counter = 1

    for section in context_packet.sections:
        if not section.text.strip():
            continue

        sentences = split_into_sentences(section.text)

        for sentence in sentences:
            requirement_type = classify_requirement_type(sentence)

            if requirement_type is None:
                continue

            confidence_score = calculate_confidence_score(
                requirement_type,
                sentence
            )

            validation_status, validation_notes = validate_requirement(
                confidence_score,
                sentence
            )

            change = RegulatoryChange(
                change_id=f"CHG-{change_counter:03}",
                document_id=context_packet.document_id,
                section_id=section.section_id,
                aggregation_group=f"AGG-{requirement_type.upper()}",
                requirement_text=sentence,
                requirement_type=requirement_type,
                confidence_score=confidence_score,
                validation_status=validation_status,
                validation_notes=validation_notes,
                extraction_method="rule_based",
                llm_model=None,
                evidence=ChangeEvidence(
                    evidence_id=section.evidence.evidence_id,
                    page_number=section.page_number,
                    section_id=section.section_id,
                    bounding_box=(
                        section.evidence.bounding_box.model_dump()
                        if section.evidence.bounding_box
                        else None
                    )
                )
            )

            changes.append(change)
            change_counter += 1

    return ChangeRegister(
        document_id=context_packet.document_id,
        total_changes=len(changes),
        extraction_method="rule_based",
        llm_model=None,
        extraction_summary=(
            f"Extracted {len(changes)} regulatory changes using "
            "rule-based sentence classification."
        ),
        
        changes=changes
    )