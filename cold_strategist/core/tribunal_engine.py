from typing import Dict, Any
from cold_strategist.core.tribunal_weights import TRIBUNAL_WEIGHTS


def tribunal_vote(outputs: Dict[str, Dict[str, Any]]) -> str:
    """
    Weighted tribunal vote. Expects outputs: minister_id -> {"content": dict, "confidence": float}
    Returns: "PROCEED" | "HALT" | "DEADLOCK"
    """
    score = 0.0

    for o in outputs.values():
        minister_id = o.get("minister_id")
        weight = TRIBUNAL_WEIGHTS.get(minister_id, 1.0)
        content = o.get("content", {}) or {}
        confidence = float(o.get("confidence", 0.0) or 0.0)

        proceed = bool(content.get("proceed") is True)

        if proceed:
            score += weight * confidence
        else:
            score -= weight * confidence

    if score > 0.5:
        return "PROCEED"
    if score < -0.5:
        return "HALT"

    return "DEADLOCK"


def tribunal_decision(outputs: Dict[str, Dict[str, Any]], disagreement: float) -> Dict[str, Any]:
    verdict = tribunal_vote(outputs)
    return {
        "decision": "TRIBUNAL",
        "verdict": verdict,
        "disagreement": disagreement,
        "sources": list(outputs.keys()),
    }
