"""Phase3 / tribunal facade for decision module.

This file provides the canonical `phase3` import path and delegates to
existing tribunal implementations.
"""

from importlib import import_module


def _load():
    candidates = (
        "cold_strategist.darbar.tribunal",
        "cold_strategist.core.tribunal_engine",
        "cold_strategist.core.tribunal_rules",
    )
    for name in candidates:
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def adjudicate(*args, **kwargs):
        raise RuntimeError("No tribunal implementation available")
else:
    for _n in dir(_impl):
        if _n.startswith("_"):
            continue
        globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
