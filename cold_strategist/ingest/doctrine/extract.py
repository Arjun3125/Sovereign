"""Canonical doctrine extraction facade.

Exports deterministic principle/doctrine extraction while avoiding
calling LLM-based implementations during the migration.
"""

try:
    # Try new locations first
    from cold_strategist.ingest.core.phase2_doctrine import *
    from cold_strategist.ingest.core.principle_extractor import *
except Exception:
    try:
        from cold_strategist.core.ingest.phase2_doctrine import *
        from cold_strategist.core.ingest.principle_extractor import *
    except Exception:
        def extract_principles(*args, **kwargs):
            raise RuntimeError("No doctrine/principle extractor available")

__all__ = [name for name in globals() if not name.startswith("_")]
