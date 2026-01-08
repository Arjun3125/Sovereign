"""Canonical validators for ingested doctrine and metadata.

Delegates to existing validator implementations where available.
"""

try:
    from cold_strategist.ingest.core.validators import *
except Exception:
    try:
        from cold_strategist.core.ingest.validators import *
    except Exception:
        def validate(*args, **kwargs):
            raise RuntimeError("No validators available")

__all__ = [name for name in globals() if not name.startswith("_")]
"""Validation utilities for ingest schemas and invariants.

Keep validation deterministic and independent of external LLMs.
"""
from typing import Any, Dict


def validate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform lightweight validation and return the (possibly annotated) data.

    This function is intentionally conservative: it asserts basic shapes
    and returns data unchanged when validation passes.
    """
    if not isinstance(data, dict):
        raise ValueError("validated data must be a dict")
    # Minimal shape check
    if "doctrines" in data and not isinstance(data["doctrines"], list):
        raise ValueError("doctrines must be a list")
    return data
"""Validators shim exposing ValidationError for legacy imports.
"""
try:
    from cold_strategist.ingest.core.validators import ValidationError  # type: ignore
except Exception:
    class ValidationError(Exception):
        pass

__all__ = ["ValidationError"]
