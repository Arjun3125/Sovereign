"""Flow control modes facade (war / quick).

Delegates to existing war/quick implementations.
"""

from importlib import import_module


def _load_candidates():
    for name in (
        "cold_strategist.core.orchestrator.war_mode",
        "cold_strategist.core.orchestrator.war_mode",
        "cold_strategist.quick.quick_engine",
    ):
        try:
            yield import_module(name)
        except Exception:
            continue


for _mod in _load_candidates():
    for _n in dir(_mod):
        if _n.startswith("_"):
            continue
        if _n not in globals():
            globals()[_n] = getattr(_mod, _n)

if "war_mode" not in globals():
    def war_mode(*args, **kwargs):
        raise RuntimeError("No war_mode available")

if "quick_mode" not in globals():
    def quick_mode(*args, **kwargs):
        raise RuntimeError("No quick_mode available")

__all__ = [n for n in globals() if not n.startswith("_")]
