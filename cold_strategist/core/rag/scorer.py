import re


def score(query: str, principle: dict, shelf_weight: float) -> float:
    if not query or not principle:
        return 0.0
    q = re.findall(r"\w+", query.lower())
    p = re.findall(r"\w+", principle.get("principle", "").lower())
    overlap = sum(1 for w in q if w in p)
    return float(overlap) * float(shelf_weight)
