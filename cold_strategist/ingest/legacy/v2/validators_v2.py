"""
Validators for Ingestion v2 two-phase compiler.

Strict schema validation for Phase-1 and Phase-2 outputs.
"""
from typing import Dict, Any, List


class ValidationError(Exception):
    """Schema validation failed."""
    pass


# Fixed 15 domains (must match prompts_v2.py)
DOMAINS = set([
    "Strategy",
    "Power",
    "Conflict & Force",
    "Deception",
    "Psychology",
    "Leadership",
    "Organization & Discipline",
    "Intelligence & Information",
    "Timing",
    "Risk & Survival",
    "Resources & Logistics",
    "Law & Order",
    "Morality & Legitimacy",
    "Diplomacy & Alliances",
    "Adaptation & Change",
])


def validate_phase1(data: dict) -> bool:
    """
    Validate Phase-1 output (book structure).

    Raises:
        ValidationError: If schema is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Phase-1 output must be a dict")

    # Check required keys
    if "chapters" not in data:
        raise ValidationError("Phase-1 output missing 'chapters' key")

    chapters = data["chapters"]
    if not isinstance(chapters, list) or len(chapters) == 0:
        raise ValidationError("Phase-1 'chapters' must be a non-empty list")

    # Validate each chapter
    for i, ch in enumerate(chapters, 1):
        if not isinstance(ch, dict):
            raise ValidationError(f"Chapter {i} must be a dict")

        # Check required fields
        for field in ["chapter_index", "chapter_title", "chapter_text"]:
            if field not in ch:
                raise ValidationError(f"Chapter {i} missing '{field}'")

        # Check chapter_index is sequential
        if ch["chapter_index"] != i:
            raise ValidationError(f"Chapter {i} has wrong index: {ch['chapter_index']} (expected {i})")

        # Check chapter_text is non-empty string
        if not isinstance(ch["chapter_text"], str) or len(ch["chapter_text"].strip()) == 0:
            raise ValidationError(f"Chapter {i} has empty or invalid chapter_text")

    return True


def validate_phase2(data: dict) -> bool:
    """
    Validate Phase-2 output (doctrine).

    Raises:
        ValidationError: If schema is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Phase-2 output must be a dict")

    # Check required keys
    required = ["chapter_index", "chapter_title", "domains", "principles", "rules", "claims", "warnings", "cross_references"]
    for key in required:
        if key not in data:
            raise ValidationError(f"Phase-2 output missing '{key}' key")

    # Validate domains
    domains = data["domains"]
    if not isinstance(domains, list):
        raise ValidationError("'domains' must be a list")
    for domain in domains:
        if domain not in DOMAINS:
            raise ValidationError(f"Invalid domain: {domain} (not in allowed list)")

    # Validate all list fields contain strings only
    list_fields = ["principles", "rules", "claims", "warnings"]
    for field in list_fields:
        if not isinstance(data[field], list):
            raise ValidationError(f"'{field}' must be a list")
        for item in data[field]:
            if not isinstance(item, str) or len(item.strip()) == 0:
                raise ValidationError(f"'{field}' contains non-string or empty item")

    # Validate cross_references
    cross_refs = data["cross_references"]
    if not isinstance(cross_refs, list):
        raise ValidationError("'cross_references' must be a list")
    for ref in cross_refs:
        if not isinstance(ref, int):
            raise ValidationError(f"cross_reference must be integer, got: {type(ref)}")

    return True

