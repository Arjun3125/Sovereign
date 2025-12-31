from typing import Dict, Any
from core.memory.memory_store import MemoryStore


def minister_reliability_matrix() -> Dict[str, Any]:
    """Compute simple reliability stats per minister from MemoryStore events.

    Returns accuracy estimate and false positive/negative heuristics.
    """
    store = MemoryStore()
    events = store.load_events()

    stats = {}
    for e in events:
        ministers = getattr(e, "ministers_called", []) or []
        # outcome: treat outcome_result as success/failure
        outcome = getattr(e, "outcome_result", None)
        for m in ministers:
            s = stats.setdefault(m, {"seen": 0, "correct": 0, "false_positive": 0, "false_negative": 0})
            s["seen"] += 1
            if outcome == "success":
                s["correct"] += 1
            elif outcome == "failure":
                s["false_positive"] += 1

    # Convert to percentages
    for m, v in stats.items():
        seen = v["seen"]
        v["accuracy"] = (v["correct"] / seen) if seen else None

    return stats
