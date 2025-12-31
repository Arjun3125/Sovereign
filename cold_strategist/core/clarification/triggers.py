from typing import List, Dict, Any


def needs_clarification(context: Dict[str, Any], interventions: List[Dict[str, Any]], resolution: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []

    if isinstance(context, dict) and context.get("reversibility") == "irreversible":
        reasons.append("irreversible")

    if isinstance(resolution, dict) and resolution.get("resolution") == "tradeoffs":
        reasons.append("conflict_unresolved")

    if isinstance(state, dict) and float(state.get("emotional_load", 0.0)) > 0.6:
        reasons.append("high_emotion")

    if any(float(i.get("confidence", 1.0)) < 0.5 for i in (interventions or [])):
        reasons.append("low_confidence")

    return reasons
