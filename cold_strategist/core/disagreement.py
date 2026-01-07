from typing import Dict, Any


def compute_disagreement(outputs: Dict[str, Dict[str, Any]]) -> float:
    """Compute a simple disagreement metric [0..1].
    Uses proceed flag majority distance heuristic.
    """
    if not outputs:
        return 1.0

    proceed_vals = []
    for o in outputs.values():
        content = o.get("content", {}) if isinstance(o, dict) else getattr(o, "content", {})
        proceed = bool(content.get("proceed") is True)
        proceed_vals.append(1 if proceed else 0)

    ones = sum(proceed_vals)
    total = len(proceed_vals)
    majority_frac = max(ones/total, 1 - ones/total)
    disagreement = 1.0 - majority_frac
    return float(disagreement)
