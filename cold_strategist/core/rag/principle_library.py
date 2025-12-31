import os
import yaml
from typing import List
from core.rag.principle_store import Principle


def _confidence_weight(principle: Principle, mode: str) -> float:
    # Simple deterministic decay/weighting by mode
    if mode == "war":
        return 1.0
    if mode == "quick":
        return 0.7
    return 0.9


class PrincipleLibrary:
    def __init__(self, principles_dir: str = None):
        if principles_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            principles_dir = os.path.join(project_root, "books", "principles")

        self.principles_dir = principles_dir
        self._principles: List[Principle] = self._load_all()

    def _load_all(self) -> List[Principle]:
        principles = []
        if not os.path.exists(self.principles_dir):
            return principles

        for fn in os.listdir(self.principles_dir):
            if not fn.endswith(".yaml"):
                continue
            path = os.path.join(self.principles_dir, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = yaml.safe_load(f) or []
                    for it in items:
                        try:
                            p = Principle(
                                id=it.get("id"),
                                text=it.get("text"),
                                pattern=it.get("pattern", ""),
                                application_space=it.get("application_space", []),
                                contraindications=it.get("contraindications", []),
                                source=it.get("source", {}),
                                shelves=it.get("shelves", []),
                                minister_affinity=it.get("minister_affinity", {}),
                                timeless=bool(it.get("timeless", False)),
                                published_year=int(it.get("published_year", 0)),
                            )
                            principles.append(p)
                        except Exception:
                            continue
            except Exception:
                continue

        return principles

    def query(self, shelves: List[str], minister: str, mode: str = "standard") -> List[Principle]:
        shelf_set = set(shelves)
        candidates = [p for p in self._principles if shelf_set.intersection(p.shelves)]
        return self._rank(candidates, minister, mode)

    def _rank(self, principles: List[Principle], minister: str, mode: str) -> List[Principle]:
        scored = []
        for p in principles:
            affinity = p.minister_affinity.get(minister, 0.4)
            decay = _confidence_weight(p, mode)
            scored.append((affinity * decay, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]
