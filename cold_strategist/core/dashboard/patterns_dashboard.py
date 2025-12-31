from typing import Dict, Any, List
from core.memory.memory_store import MemoryStore


def patterns_overview(min_occurrences: int = 2) -> List[Dict[str, Any]]:
    """Return recurring patterns with counts and basic metrics.

    Uses MemoryStore.load_patterns() when available; otherwise returns empty list.
    """
    store = MemoryStore()
    try:
        patterns = store.load_patterns()
    except Exception:
        return []

    overview = []
    for p in patterns:
        # pattern is expected to have: pattern_name, frequency, domain, last_outcome
        count = getattr(p, "frequency", 0)
        if count < min_occurrences:
            continue

        avg_cost = getattr(p, "last_outcome", None)
        overview.append({
            "pattern": getattr(p, "pattern_name", "unknown"),
            "occurrences": count,
            "domain": getattr(p, "domain", "unknown"),
            "avg_cost": avg_cost,
            "notes": getattr(p, "description", ""),
        })

    # Sort by occurrences desc
    overview.sort(key=lambda x: x["occurrences"], reverse=True)
    return overview
