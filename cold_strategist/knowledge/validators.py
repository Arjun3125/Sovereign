"""Canonical validators facade for knowledge schemas.

Delegates to available validators under doctrine/core/knowledge.
"""

from importlib import import_module


def _load():
    candidates = (
        "cold_strategist.doctrine.validators",
        "cold_strategist.core.knowledge.validators",
        "cold_strategist.knowledge.validators",
    )
    for name in candidates:
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def validate(*args, **kwargs):
        raise RuntimeError("No knowledge validators available")
else:
    for _n in dir(_impl):
        if _n.startswith("_"):
            continue
        globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
