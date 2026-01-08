"""Top-level chapters / structure facade."""

from importlib import import_module


def _load():
    for name in (
        "cold_strategist.ingest.structure.chapters",
        "cold_strategist.ingest.structure",
        "cold_strategist.core.ingest.structural_chunker",
        "cold_strategist.ingest.core.structural_chunker",
    ):
        try:
            return import_module(name)
        except Exception:
            continue
    return None


_impl = _load()

if _impl is None:
    def detect_chapters(*args, **kwargs):
        raise RuntimeError("No chapter detection implementation available")
else:
    if hasattr(_impl, "detect_chapters"):
        detect_chapters = getattr(_impl, "detect_chapters")
    else:
        for _n in dir(_impl):
            if _n.startswith("_"):
                continue
            globals()[_n] = getattr(_impl, _n)

__all__ = [n for n in globals() if not n.startswith("_")]
