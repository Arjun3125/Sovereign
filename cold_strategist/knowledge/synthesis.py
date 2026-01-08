"""Knowledge synthesis facade.

Note: knowledge SHOULD NOT perform reasoning. If reasoning logic exists,
it should be moved to `cold_strategist.debate` or `cold_strategist.decision`.
This module delegates to existing synthesis implementations if present.
"""

from importlib import import_module


def _load():
    for name in (
        "cold_strategist.core.knowledge.synthesis",
        "cold_strategist.knowledge.synthesis",
        "cold_strategist.doctrine.synthesis",
    ):
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def synthesize(*args, **kwargs):
        raise RuntimeError("No knowledge synthesis implementation available")
else:
    for _n in dir(_impl):
        if _n.startswith("_"):
            continue
        globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
