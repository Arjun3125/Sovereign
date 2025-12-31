from typing import Tuple, Dict, Any


def apply_answer(context: Dict[str, Any], state: Dict[str, Any], answer: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not isinstance(context, dict):
        context = {"raw_text": str(context), "notes": []}

    context.setdefault("notes", []).append(str(answer))

    if not isinstance(state, dict):
        state = {"clarity": 0.0, "emotional_load": 0.0}

    state["clarity"] = min(1.0, float(state.get("clarity", 0.0)) + 0.15)
    state["emotional_load"] = max(0.0, float(state.get("emotional_load", 0.0)) - 0.1)

    return context, state
