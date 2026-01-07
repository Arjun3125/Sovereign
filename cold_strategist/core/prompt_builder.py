from typing import Any
from cold_strategist.core.ministers import MinisterConstraint


def build_minister_prompt(minister: MinisterConstraint, chapter_text: str) -> str:
    """
    Build a strict, worldview-locked prompt for phase-2 extraction for a single minister.
    The prompt forces JSON output and a silence signal when evidence is insufficient.
    """
    forbidden = ", ".join(sorted(minister.forbidden)) if minister.forbidden else "none"
    allowed = ", ".join(sorted(minister.allowed)) if minister.allowed else "none"
    required = minister.output_shape.get("required_fields", [])
    optional = minister.output_shape.get("optional_fields", [])

    prompt = f"""
You are the Minister of {minister.id.upper()}.

WORLDVIEW (MANDATORY):
{minister.worldview}

FORBIDDEN CONCEPTS (DO NOT APPEAR):
{forbidden}

ALLOWED FOCUS (ONLY THESE):
{allowed}

OUTPUT SHAPE (STRICT JSON):
Required fields: {required}
Optional fields: {optional}

CONFIDENCE RULE:
If evidence is insufficient for the required fields, output EXACTLY: {{"silence": true}}

CHAPTER TEXT:
{chapter_text}

Return ONLY valid JSON in a single reply. No narrative, no justification outside the specified fields.
"""
    return prompt
