from pathlib import Path
from typing import List, Dict, Any
from core.rag.vector_store import VectorStore
from core.rag.scoring import ScoringConfig, compute_confidence


class ConfidentRetriever:
    def __init__(self, minister: str, config: ScoringConfig = None):
        self.minister = minister
        self.config = config or ScoringConfig()
        idx_path = Path("knowledge/index") / f"{minister.lower()}.index"
        try:
            self.store = VectorStore.load(idx_path)
        except Exception:
            # empty store fallback
            self.store = VectorStore(path=idx_path)

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            hits = self.store.search(query, top_k=k)
        except Exception:
            hits = []

        for h in hits:
            meta = h.get("meta", {})
            sim = float(h.get("similarity", 0.0))
            book = meta.get("book") or ""
            conf = compute_confidence(sim, book, self.minister, self.config)
            results.append({
                "text": h.get("text"),
                "meta": meta,
                "similarity": sim,
                "confidence": round(conf, 3),
            })

        # sort by confidence desc
        results.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        return results
