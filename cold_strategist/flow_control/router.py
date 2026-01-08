"""Canonical router facade for flow control."""

from importlib import import_module


def _load():
    for name in (
        "cold_strategist.orchestrator.router",
        "cold_strategist.core.orchestrator.router",
        "cold_strategist.orchestrator.router",
    ):
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def route(*args, **kwargs):
        raise RuntimeError("No router implementation found")
else:
    for n in dir(_impl):
        if n.startswith("_"):
            continue
        globals()[n] = getattr(_impl, n)

__all__ = [n for n in globals() if not n.startswith("_")]
