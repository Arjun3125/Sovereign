"""Canonical ingest pipeline facade.

This module provides a single canonical entrypoint for ingestion.
It delegates to the best available implementation found in the tree
so we don't duplicate behavior during the migration.
"""

from importlib import import_module
from typing import Any


_candidates = (
    "cold_strategist.ingest.core.ingest",
    "cold_strategist.ingest.core.ingest_v2",
    "cold_strategist.core.ingest.ingest",
    "cold_strategist.core.ingest.ingest_v2",
)


def _load_impl():
    for name in _candidates:
        try:
            mod = import_module(name)
        except Exception:
            continue
        # prefer a callable named `ingest` or `ingest_v2` or fallback to module
        if hasattr(mod, "ingest"):
            return getattr(mod, "ingest")
        if hasattr(mod, "ingest_v2"):
            return getattr(mod, "ingest_v2")
        return mod
    raise RuntimeError("No ingest implementation found; check your install or legacy placement")


_impl = None


def ingest(*args, **kwargs) -> Any:
    """Canonical ingest entrypoint.

    Delegates to the actual implementation discovered in the repo.
    Callers should import `cold_strategist.ingest.pipeline.ingest`.
    """
    global _impl
    if _impl is None:
        _impl = _load_impl()

    if callable(_impl):
        return _impl(*args, **kwargs)

    # If module-like impl, try to call a reasonable symbol
    if hasattr(_impl, "run"):
        return _impl.run(*args, **kwargs)
    raise RuntimeError("Loaded ingest implementation is not callable")
