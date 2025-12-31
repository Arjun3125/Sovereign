from typing import List
from dataclasses import dataclass
from core.rag.citation_conflicts import CONFLICT_TYPES


@dataclass
class Claim:
    id: str
    assertion_strength: float
    confidence_modifier: float
    context_tags: set
    application_space: set
    mode: str
    source_count: int
    counter_citations: List[dict]


def detect_conflicts(claim: Claim) -> List[str]:
    flags = []

    if claim.assertion_strength > claim.confidence_modifier + 0.2:
        flags.append("OVERCONFIDENCE")

    if not claim.context_tags.intersection(claim.application_space):
        flags.append("MISAPPLICATION")

    if claim.confidence_modifier < 0.8 and claim.mode == "war":
        flags.append("STALE_EVIDENCE")

    if claim.source_count == 1:
        flags.append("SINGLE_SOURCE")

    if claim.counter_citations:
        flags.append("COUNTEREVIDENCE")

    return flags
