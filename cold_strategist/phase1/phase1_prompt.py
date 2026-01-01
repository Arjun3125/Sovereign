import json
from typing import List
from .schema import Phase1Response


PROMPT = """
You are Phase-1 assistant. Your job is to analyze a short `situation` text and produce a concise, structured JSON response matching the specified schema exactly.

Schema (Phase1Response):
- status: one of "OK", "NEEDS_CONTEXT", "ERROR"
- reasoning: short explanation (1-5 sentences)
- confidence: float between 0.0 and 1.0
- decision: object describing the recommended decision and parameters
- actions: optional array of follow-up actions (objects)

REQUIREMENTS:
- Return ONLY a single JSON object and nothing else (no markdown, no backticks, no commentary).
- Fields must exactly match the schema types.
- Use numbers for `confidence` (0.0-1.0).
- If the `situation` is empty or insufficient, set `status` to "NEEDS_CONTEXT" and provide a short `reasoning` explaining what is missing.
- If an internal failure occurs, set `status` to "ERROR" and populate `reasoning`.

EXAMPLES: see `EXAMPLES` variable in this module.
"""

EXAMPLES: List[str] = [
    # 1: Clear actionable situation
    json.dumps({
        "status": "OK",
        "reasoning": "Sufficient details provided and actors identified.",
        "confidence": 0.87,
        "decision": {"action": "engage", "parameters": {"level": "limited"}},
        "actions": [
            {"type": "NOTIFY", "description": "Inform commander of limited engagement", "target": "commander"}
        ],
        "metadata": {"source": "example"}
    }),

    # 2: Missing context
    json.dumps({
        "status": "NEEDS_CONTEXT",
        "reasoning": "Location and timeframe missing; cannot assess urgency.",
        "confidence": 0.0,
        "decision": {"action": "none", "parameters": {}},
        "actions": [{"type": "GATHER_INFO", "description": "Request location and timeframe from reporter"}],
    }),

    # 3: Internal error
    json.dumps({
        "status": "ERROR",
        "reasoning": "Parsing failed due to malformed input.",
        "confidence": 0.0,
        "decision": {"action": "none", "parameters": {}},
    }),

    # 4: Low-confidence, monitoring suggestion
    json.dumps({
        "status": "OK",
        "reasoning": "Some indicators point to potential hostile intent but evidence is weak.",
        "confidence": 0.35,
        "decision": {"action": "monitor", "parameters": {"period": "2h"}},
        "actions": [{"type": "GATHER_INFO", "description": "Increase surveillance for 2 hours"}],
    }),
]


def validate_response(raw: str) -> Phase1Response:
    """Parse and validate a raw LLM response string.

    - Accepts raw string (expected to be JSON).
    - Raises ValueError on parse error or pydantic.ValidationError on schema mismatch.
    - Returns a Phase1Response instance on success.
    """
    # Strip common markdown fences or accidental surrounding text
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # remove leading fence and optional language tag
        parts = cleaned.split("\n", 1)
        if len(parts) > 1:
            cleaned = parts[1]
        # remove trailing fence
        if cleaned.rfind("```") != -1:
            cleaned = cleaned[: cleaned.rfind("```")]
    cleaned = cleaned.strip()

    try:
        obj = json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Response is not valid JSON: {e}")

    # Validate using pydantic v2 if available, otherwise v1 compatible parse
    try:
        if hasattr(Phase1Response, "model_validate"):
            validated = Phase1Response.model_validate(obj)
        else:
            validated = Phase1Response.parse_obj(obj)
    except Exception as e:
        # Re-raise for caller to handle; preserve original exception
        raise

    return validated
