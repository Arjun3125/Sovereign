"""Persistence facade for writing ingest outputs to workspace/storage."""

from importlib import import_module


def _load():
    candidates = (
        "cold_strategist.ingest.core.persist_book",
        "cold_strategist.core.ingest.persist_book",
        "cold_strategist.ingest.core.storage",
        "cold_strategist.core.ingest.storage",
    )
    for name in candidates:
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def persist_book(*args, **kwargs):
        raise RuntimeError("No persist implementation available")
else:
    if hasattr(_impl, "persist_book"):
        persist_book = getattr(_impl, "persist_book")
    else:
        for _n in dir(_impl):
            if _n.startswith("_"):
                continue
            globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
