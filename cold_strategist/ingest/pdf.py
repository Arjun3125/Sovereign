"""Top-level pdf extractor facade.

Delegates to canonical `cold_strategist.ingest.extract.pdf` or falls back
to older locations.
"""

from importlib import import_module


def _load():
    candidates = (
        "cold_strategist.ingest.extract.pdf",
        "cold_strategist.ingest.extractors.pdf",
        "cold_strategist.core.ingest.extract_pdf",
        "cold_strategist.ingest.core.extract_pdf",
    )
    for name in candidates:
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def extract_pdf(*args, **kwargs):
        raise RuntimeError("No PDF extractor available")
else:
    if hasattr(_impl, "extract_pdf"):
        extract_pdf = getattr(_impl, "extract_pdf")
    else:
        # export all available helpers
        for _n in dir(_impl):
            if _n.startswith("_"):
                continue
            globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
