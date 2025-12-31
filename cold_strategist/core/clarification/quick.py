def quick_clarify(context: dict, state: dict):
    """Decide whether a single quick clarification should be asked.

    Rules (hard):
    - Max 1 question
    - Only if stakes != 'trivial'
    - Only if ambiguity detected (clarity low)
    - Only if state.urgency >= 0.6
    - If reversible and emotional load low, skip
    - Owner is 'N'
    """
    urgency = float(state.get("urgency", 0.0))
    if urgency < 0.6:
        return None

    if context.get("reversibility") == "reversible" and float(state.get("emotional_load", 0.0)) < 0.5:
        return None

    # ambiguity detection: low clarity
    clarity = float(state.get("clarity", 0.0))
    if clarity >= 0.7:
        return None

    if context.get("stakes", "nontrivial") == "trivial" or state.get("stakes") == "trivial":
        return None

    return {
        "owner": "N",
        "goal": "preference_resolution",
        "max_questions": 1,
    }
