"""Canonical debate engine facade.

Debate must not perform decision-making or call LLMs; this facade
exposes the debate engine by delegating to existing implementations.
"""

from importlib import import_module


def _try_load(names):
    for name in names:
        try:
            mod = import_module(name)
            return mod
        except Exception:
            continue
    return None


_impl = _try_load((
    "cold_strategist.debate.knowledge_debate_engine",
    "cold_strategist.core.debate.debate_engine",
    "cold_strategist.core.darbar",
))


if _impl is None:
    def run_debate(*args, **kwargs):
        raise RuntimeError("No debate engine implementation found")
else:
    # Export primary functions if present
    for _name in ("run_debate", "debate", "assemble_arguments"):
        if hasattr(_impl, _name):
            globals()[_name] = getattr(_impl, _name)

    # fallback: export module-level names
    for _name in dir(_impl):
        if _name.startswith("_"):
            continue
        if _name not in globals():
            globals()[_name] = getattr(_impl, _name)

__all__ = [n for n in globals() if not n.startswith("_")]
