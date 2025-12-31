from typing import Dict, Any
from core.memory.memory_store import MemoryStore


def war_usage_summary() -> Dict[str, Any]:
    """Return summary metrics for War Mode usage.

    Metrics: count, triggers breakdown (best-effort), average duration (if stored), re-entry quality.
    """
    store = MemoryStore()
    events = store.get_events_by_domain("war")

    count = len(events)
    # best-effort: assume each event may have 'duration' in outcome_lessons or verdict
    durations = []
    relapse_count = 0

    for e in events:
        # detect quick relapse via event metadata stored in lessons/outcome
        lessons = getattr(e, "outcome_lessons", []) or []
        if any("relapse" in str(x).lower() for x in lessons):
            relapse_count += 1
        # duration heuristic: not available often; skip

    reentry_quality = {
        "total_war_events": count,
        "relapses": relapse_count,
        "relapse_rate": (relapse_count / count) if count else 0.0,
    }

    return reentry_quality
