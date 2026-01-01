"""
Schema validators for Ingestion v2.

Enforces strict invariants on Phase-1 and Phase-2 output.
"""

DOMAINS = {
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
}


class ValidationError(Exception):
    """Schema validation failed."""
    pass


def validate_phase1(data: dict) -> None:
    """
    Validate Phase-1 output structure.

    Args:
        data: Phase-1 LLM response (should be entire book structure)

    Raises:
        ValidationError: If schema violated
    """
    if not isinstance(data, dict):
        raise ValidationError("Phase-1 response must be dict")

    if "chapters" not in data:
        raise ValidationError("Missing 'chapters' key")

    chapters = data["chapters"]
    if not isinstance(chapters, list) or not chapters:
        raise ValidationError("'chapters' must be non-empty list")

    for i, ch in enumerate(chapters, 1):
        if not isinstance(ch, dict):
            raise ValidationError(f"Chapter {i} is not a dict")

        if ch.get("chapter_index") != i:
            raise ValidationError(f"Chapter {i} has wrong index: {ch.get('chapter_index')}")

        if not isinstance(ch.get("chapter_text"), str):
            raise ValidationError(f"Chapter {i} 'chapter_text' not string")

        if not isinstance(ch.get("chapter_title"), str):
            raise ValidationError(f"Chapter {i} 'chapter_title' not string")

        # CRITICAL: Reject summaries — chapter_text must be substantial (not a brief description)
        # Summaries are typically 1-3 sentences (~50-300 chars); real chapter text is much longer
        ch_text = ch.get("chapter_text", "")
        if len(ch_text) < 400:
            raise ValidationError(f"Chapter {i} text too short (likely a summary, not full chapter): {len(ch_text)} chars")


def validate_phase2(data: dict) -> None:
    """
    Validate Phase-2 output structure.

    Args:
        data: Phase-2 LLM response (doctrine for one chapter)

    Raises:
        ValidationError: If schema violated or content insufficient
    """
    if not isinstance(data, dict):
        raise ValidationError("Phase-2 response must be dict")

    # Required keys
    required = ["chapter_index", "chapter_title", "domains", "principles", "rules", "claims", "warnings", "cross_references"]
    for key in required:
        if key not in data:
            raise ValidationError(f"Missing required key: {key}")

    # Validate chapter metadata
    if not isinstance(data["chapter_index"], int):
        raise ValidationError("'chapter_index' must be int")

    if not isinstance(data["chapter_title"], str):
        raise ValidationError("'chapter_title' must be string")

    # Validate list fields (all must be lists of strings)
    string_list_fields = ["principles", "rules", "claims", "warnings", "domains"]
    for field in string_list_fields:
        if not isinstance(data[field], list):
            raise ValidationError(f"'{field}' must be list")

        for item in data[field]:
            if not isinstance(item, str):
                raise ValidationError(f"'{field}' contains non-string: {item}")

    # Validate domains are in allowed set
    for domain in data["domains"]:
        if domain not in DOMAINS:
            raise ValidationError(f"Invalid domain: {domain}")

    # Validate cross_references are integers
    if not isinstance(data["cross_references"], list):
        raise ValidationError("'cross_references' must be list")

    for ref in data["cross_references"]:
        if not isinstance(ref, int):
            raise ValidationError(f"'cross_references' contains non-int: {ref}")

    # No empty strings
    for field in string_list_fields:
        for item in data[field]:
            if item == "":
                raise ValidationError(f"Empty string in '{field}'")

    # CONTENT VALIDATION: Ensure meaningful extraction
    # Chapter should have:
    # - At least 1 domain
    # - At least 1 principle OR 1 rule (core doctrine)
    # - At least 1 claim OR 1 warning (assertions about reality)
    has_domain = len(data["domains"]) > 0
    has_core = len(data["principles"]) > 0 or len(data["rules"]) > 0
    has_content = len(data["claims"]) > 0 or len(data["warnings"]) > 0

    if not has_domain:
        raise ValidationError(
            "No domains extracted - insufficient doctrine extraction"
        )
    if not has_core:
        raise ValidationError(
            "No principles or rules - missing core doctrine"
        )
    if not has_content:
        raise ValidationError(
            "No claims or warnings - missing assertions/warnings"
        )
