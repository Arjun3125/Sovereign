from typing import Dict, Any
from core.memory.memory_store import MemoryStore


def emotional_outcome_stats() -> Dict[str, Any]:
    """Return aggregated outcomes grouped by emotional load.

    Groups: low, medium, high
    """
    store = MemoryStore()
    events = store.load_events()

    buckets = {"low": [], "medium": [], "high": []}
    for e in events:
        emo = getattr(e, "emotional_load", "low")
        if emo not in buckets:
            emo = "low"
        delta = getattr(e, "outcome_benefit", 0.0) - getattr(e, "outcome_damage", 0.0)
        buckets[emo].append(delta)

    result = {}
    for k, vals in buckets.items():
        result[k] = {
            "count": len(vals),
            "avg_outcome_delta": (sum(vals) / len(vals)) if vals else None,
        }

    return result
