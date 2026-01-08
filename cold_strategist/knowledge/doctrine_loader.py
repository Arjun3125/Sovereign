"""Facade for doctrine loading utilities."""

from importlib import import_module


def _load():
    for name in (
        "cold_strategist.doctrine.doctrine_loader",
        "cold_strategist.core.knowledge.doctrine_loader",
    ):
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def load_doctrine(*args, **kwargs):
        raise RuntimeError("No doctrine_loader available")
else:
    for _n in dir(_impl):
        if _n.startswith("_"):
            continue
        globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
