from typing import List, Dict, Any


def plan_questions(reasons: List[str], context: Dict[str, Any], ministers: List[str]) -> List[Dict[str, Any]]:
    plans: List[Dict[str, Any]] = []

    if "irreversible" in reasons:
        plans.append({
            "goal": "downside_mapping",
            "owner": "N",
            "prompt_hint": "irreversibility",
        })

    if "conflict_unresolved" in reasons:
        plans.append({
            "goal": "preference_elicitation",
            "owner": "N",
            "prompt_hint": "tradeoffs",
        })

    if "high_emotion" in reasons:
        plans.append({
            "goal": "emotion_labeling",
            "owner": "Psychology",
            "prompt_hint": "label_emotion",
        })

    if "low_confidence" in reasons:
        plans.append({
            "goal": "clarify_uncertainties",
            "owner": "N",
            "prompt_hint": "clarify_missing",
        })

    return plans
