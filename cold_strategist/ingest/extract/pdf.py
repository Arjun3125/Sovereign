"""Canonical extractor facade that delegates to existing implementation.

This keeps existing code intact while creating a single canonical
location for extractors during the migration.
"""

try:
    # Primary source (old location)
    from cold_strategist.core.ingest.extract_pdf import *
except Exception:
    try:
        from cold_strategist.ingest.core.extract_pdf import *
    except Exception:
        # Fallback: expose a clear missing implementation indicator
        def extract_pdf(*args, **kwargs):
            raise RuntimeError("No pdf extractor implementation available")

__all__ = [name for name in globals() if not name.startswith("_")]
