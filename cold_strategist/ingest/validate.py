"""Top-level validators facade for ingested doctrine and metadata."""

from importlib import import_module


def _load():
    for name in (
        "cold_strategist.ingest.validators",
        "cold_strategist.ingest.core.validators",
        "cold_strategist.core.ingest.validators",
    ):
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def validate(*args, **kwargs):
        raise RuntimeError("No ingest validators available")
else:
    for _n in dir(_impl):
        if _n.startswith("_"):
            continue
        globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
