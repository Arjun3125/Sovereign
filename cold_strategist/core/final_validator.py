from typing import Any
from cold_strategist.core.validator import validate_output
from cold_strategist.core.ministers import MinisterConstraint


def final_validate(minister: MinisterConstraint, output: Any) -> bool:
    """Stricter, final gate for minister outputs. Returns True if acceptable."""
    v = validate_output(minister, output)
    return v == "OK"
