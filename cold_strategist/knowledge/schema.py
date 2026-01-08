"""Canonical knowledge schema facade.

This module exposes a small, stable schema API for the canonical
`cold_strategist.knowledge` package. During migration it attempts to
reuse existing schema implementations (prefer `cold_strategist.core.knowledge.schema`),
but provides minimal, safe fallbacks so the package remains importable.
"""
from typing import Any, Dict

__all__ = []


def _try_import_module(mod_path: str) -> Any:
    try:
        components = mod_path.split(".")
        module = __import__(mod_path, fromlist=[components[-1]])
        return module
    except Exception:
        return None


# Preferred upstream schema implementations to try, in order.
_candidates = [
    "cold_strategist.core.knowledge.schema",
    "cold_strategist.knowledge.ingest.schema",
    "cold_strategist.doctrine.schema",
]

_loaded_from = None
for _c in _candidates:
    _m = _try_import_module(_c)
    if _m is not None:
        # Import common symbols if present
        for _name in ("KnowledgeSchema", "load_schema", "validate"):
            if hasattr(_m, _name):
                globals()[_name] = getattr(_m, _name)
                if _name not in __all__:
                    __all__.append(_name)
        _loaded_from = _c
        break


# If nothing was imported, provide minimal safe implementations so
# `from cold_strategist.knowledge import *` succeeds during migration.
if not __all__:
    from dataclasses import dataclass

    @dataclass
    class KnowledgeSchema:
        """Minimal placeholder schema object."""
        name: str = "minimal"


    def load_schema(path: str) -> Dict[str, Any]:
        """Load a schema from `path`.

        This is a minimal no-op fallback returning an empty dict.
        """
        return {}


    def validate(instance: Any, schema: Dict[str, Any]) -> bool:
        """Validate `instance` against `schema`.

        The fallback always returns True (lenient) so callers relying on
        import-time availability do not fail. Replace with a strict
        implementation once canonical schema exists.
        """
        return True

    __all__ = ["KnowledgeSchema", "load_schema", "validate"]


# Expose a small diagnostic variable for debugging/migration tracing.
_LOADED_FROM = _loaded_from
