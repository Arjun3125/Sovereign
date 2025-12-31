from typing import Dict, Any, List
from core.memory.memory_store import MemoryStore


def trajectory_drift_report(declared_goals: List[str]) -> Dict[str, Any]:
    """Compare declared long-term goals to historical events to detect drift.

    This is a heuristic view: caller supplies declared goals to compare against events.
    """
    store = MemoryStore()
    events = store.load_events()

    # Heuristic: count events whose verdict_position mentions goal keywords
    coverage = {g: 0 for g in declared_goals}
    for e in events:
        vp = getattr(e, "verdict_position", "").lower()
        for g in declared_goals:
            if g.lower() in vp:
                coverage[g] += 1

    # Simple drift metric: declared goals with low coverage
    drift = {g: {"coverage": coverage[g], "drift": coverage[g] == 0} for g in declared_goals}

    return {
        "declared_goals": declared_goals,
        "coverage": coverage,
        "drift": drift,
    }
