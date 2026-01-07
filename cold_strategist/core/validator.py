import json
from typing import Any
from cold_strategist.core.ministers import MinisterConstraint


def validate_output(minister: MinisterConstraint, output: Any) -> str:
    """
    Validate a minister's output against its constraint.

    Returns:
      - "SILENCE" if minister explicitly signalled silence
      - "OK" if output conforms
      - "INVALID" otherwise
    """
    # If LLM returned raw string, try to parse JSON
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except Exception:
            return "INVALID"

    if not isinstance(output, dict):
        return "INVALID"

    if output.get("silence") is True:
        return "SILENCE"

    # Required fields check
    for field in minister.output_shape.get("required_fields", []):
        if field not in output:
            return "INVALID"

    # Forbidden concepts check (string scan)
    output_text = json.dumps(output).lower()
    for forbidden in minister.forbidden:
        if forbidden.lower() in output_text:
            return "INVALID"

    return "OK"
