from typing import Dict, Any
from core.memory.memory_store import MemoryStore


def override_heatmap() -> Dict[str, Any]:
    """Return stats about overrides: counts per minister and outcome deltas.

    Best-effort: uses MemoryStore.get_overridden_events() and outcome fields.
    """
    store = MemoryStore()
    events = store.get_overridden_events()

    by_minister = {}
    total = len(events)
    outcome_deltas = []

    for e in events:
        key = e.verdict_position or "unknown"
        by_minister.setdefault(key, {"count": 0, "deltas": []})
        by_minister[key]["count"] += 1

        # outcome delta heuristic: benefit - damage
        delta = getattr(e, "outcome_benefit", 0.0) - getattr(e, "outcome_damage", 0.0)
        by_minister[key]["deltas"].append(delta)
        outcome_deltas.append(delta)

    summary = {m: {"count": v["count"], "avg_outcome_delta": (sum(v["deltas"]) / len(v["deltas"])) if v["deltas"] else None} for m, v in by_minister.items()}

    overall = {
        "total_overrides": total,
        "per_minister": summary,
        "avg_outcome_delta": (sum(outcome_deltas) / len(outcome_deltas)) if outcome_deltas else None,
    }

    return overall
