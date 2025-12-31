from typing import List, Tuple


def book_effectiveness(entries: List[Tuple[float, float]]) -> float:
    if not entries:
        return 0.5
    weighted = sum((r * (o if o is not None else 0.0)) for r, o in entries)
    norm = sum(r for r, _ in entries)
    return float(weighted / max(1e-6, norm))
