from pathlib import Path
from typing import Any, Dict
import json


DEFAULT_WEIGHTS = {
    "similarity": 0.45,
    "source": 0.20,
    "affinity": 0.15,
    "outcome": 0.15,
    "decay": 0.05,
}


class ScoringConfig:
    def __init__(self, weights: Dict[str, float] = None, enable_decay: bool = True):
        self.w = weights or DEFAULT_WEIGHTS
        self.enable_decay = enable_decay

    def _read_yaml(self, path: Path):
        try:
            import yaml
            return yaml.safe_load(path.read_text(encoding='utf-8'))
        except Exception:
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                return {}

    def book_reliability(self, book: str) -> float:
        md = Path("knowledge/books/metadata") / f"{book}.yaml"
        if md.exists():
            data = self._read_yaml(md)
            return float(data.get("source_reliability", 0.5))
        return 0.5

    def minister_affinity(self, minister: str, book: str) -> float:
        shelf = Path("knowledge/shelves") / f"{minister.lower()}.yaml"
        if shelf.exists():
            data = self._read_yaml(shelf)
            allowed = data.get("allowed_books") or {}
            # allowed_books may be list or mapping
            if isinstance(allowed, dict):
                return float(allowed.get(book, {}).get("affinity", allowed.get(book, 0.5)))
            if isinstance(allowed, list):
                return 0.9 if book in allowed else 0.1
        return 0.5

    def outcome_score(self, minister: str, book: str) -> float:
        # read simple outcomes file if exists
        p = Path("data/outcomes") / f"{book}.json"
        try:
            if p.exists():
                d = json.loads(p.read_text(encoding='utf-8'))
                # d expected to have rolling_avg between -1 and +1
                val = float(d.get("rolling_effectiveness", 0.0))
                # normalize to 0..1
                return max(0.0, min(1.0, 0.5 + 0.5 * val))
        except Exception:
            pass
        return 0.5

    def staleness_penalty(self, book: str) -> float:
        # simple: older books have higher staleness
        md = Path("knowledge/books/metadata") / f"{book}.yaml"
        try:
            if md.exists():
                data = self._read_yaml(md)
                year = int(data.get("year", 0) or 0)
                if year == 0:
                    return 0.0
                import datetime
                age = datetime.datetime.utcnow().year - year
                return min(1.0, age / 100.0)
        except Exception:
            pass
        return 0.0


def compute_confidence(similarity: float, book: str, minister: str, config: ScoringConfig) -> float:
    src = config.book_reliability(book)
    affinity = config.minister_affinity(minister, book)
    outcome = config.outcome_score(minister, book)
    staleness = config.staleness_penalty(book)

    score = (
        config.w.get("similarity", 0.0) * float(similarity)
        + config.w.get("source", 0.0) * float(src)
        + config.w.get("affinity", 0.0) * float(affinity)
        + config.w.get("outcome", 0.0) * float(outcome)
    )

    if config.enable_decay:
        score -= config.w.get("decay", 0.0) * float(staleness)

    return max(0.0, min(1.0, float(score)))
