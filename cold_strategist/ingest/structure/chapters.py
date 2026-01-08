"""Canonical chapter detection facade.

Delegates to existing structural chunker implementation during migration.
"""

try:
    from cold_strategist.core.ingest.structural_chunker import *
except Exception:
    try:
        from cold_strategist.ingest.core.structural_chunker import *
    except Exception:
        def detect_chapters(*args, **kwargs):
            raise RuntimeError("No chapter detection implementation available")

__all__ = [name for name in globals() if not name.startswith("_")]
