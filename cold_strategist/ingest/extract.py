"""Top-level doctrine extraction facade.

Delegates to `cold_strategist.ingest.doctrine.extract` or legacy locations.
"""

from importlib import import_module


def _load():
    candidates = (
        "cold_strategist.ingest.doctrine.extract",
        "cold_strategist.ingest.doctrine",
        "cold_strategist.core.ingest.phase2_doctrine",
        "cold_strategist.ingest.core.phase2_doctrine",
    )
    for name in candidates:
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def extract_principles(*args, **kwargs):
        raise RuntimeError("No doctrine/principle extractor available")
else:
    if hasattr(_impl, "extract_principles"):
        extract_principles = getattr(_impl, "extract_principles")
    else:
        for _n in dir(_impl):
            if _n.startswith("_"):
                continue
            globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
