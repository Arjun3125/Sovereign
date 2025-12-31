from typing import List, Dict, Tuple


def detect_disagreement(interventions: List[Dict]) -> Tuple[bool, Dict[str, List[Dict]]]:
    """Detect whether multiple stances are present among interventions.

    Returns (conflict_flag, stances_map)
    """
    stances: Dict[str, List[Dict]] = {}
    for i in interventions:
        st = i.get("stance", "neutral")
        stances.setdefault(st, []).append(i)

    conflict = len([k for k in stances.keys() if k and k != "neutral"]) > 1
    return conflict, stances
def detect_disagreement(interventions):
    """Return (conflict_bool, stances_map).

    interventions: list of dicts with keys including 'stance'
    """
    stances = {}
    for i in interventions:
        st = i.get("stance", "unknown")
        stances.setdefault(st, []).append(i)
    conflict = len([k for k in stances.keys() if k and k != "unknown"]) > 1
    return conflict, stances
