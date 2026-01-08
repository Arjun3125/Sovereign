"""Canonical registry facade for `cold_strategist.knowledge`.

Delegates to existing registry implementations (doctrine, core, or legacy)
to provide a single import surface during migration.
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
    "cold_strategist.doctrine.registry",
    "cold_strategist.core.knowledge.registry",
    "cold_strategist.knowledge.registry",
))


if _impl is None:
    def get_registry(*args, **kwargs):
        raise RuntimeError("No knowledge registry implementation found")
else:
    # export everything from the implementation module
    for _name in dir(_impl):
        if _name.startswith("_"):
            continue
        globals()[_name] = getattr(_impl, _name)

__all__ = [n for n in globals() if not n.startswith("_")]
