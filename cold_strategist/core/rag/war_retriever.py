from core.rag.retriever import RAGRetriever


class WarAwareRAGRetriever(RAGRetriever):
    """War-aware retriever: shelves should be pre-biased by ShelfBuilder with war=True."""

    def retrieve(self, query: str, minister: str, top_k: int = 5, decision_id: str = None):
        # same as base for now; shelves already biased
        return super().retrieve(query, minister, top_k=top_k, decision_id=decision_id)
"""War-aware RAG retriever wrapper.

Selects shelves according to mode and minister affinity, delegates to
`retrieve_for_minister`, and preserves decision_id for tracing.
"""
from core.rag.retriever import retrieve_for_minister
from pathlib import Path


class WarAwareRAGRetriever:
    def __init__(self, affinity_path: str = None):
        # Load affinity mapping if available
        self.affinity = {}
        if affinity_path is None:
            affinity_path = Path("core/rag/affinity.yaml")
        try:
            p = Path(affinity_path)
            if p.exists():
                try:
                    import yaml
                    with p.open("r", encoding="utf-8") as f:
                        self.affinity = yaml.safe_load(f) or {}
                except Exception:
                    self.affinity = {}
        except Exception:
            self.affinity = {}

    def retrieve(self, minister_name: str, context=None, mode: str = "standard", cap: int = 5, decision_id: str = None):
        # If minister has affinity mapping, prefer those shelves by passing through selector mode
        # For now, delegate to retrieve_for_minister and pass decision_id so traces are emitted
        return retrieve_for_minister(minister_name, context=context, mode=("war" if mode == "war" else "standard"), cap=cap, decision_id=decision_id)
