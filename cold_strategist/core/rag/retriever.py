from typing import List, Dict, Any
from core.rag.scorer import score
from core.rag.trace import log_rag_trace


class RAGRetriever:
    def __init__(self, shelves: List[Dict[str, Any]]):
        self.shelves = shelves or []

    def retrieve(self, query: str, minister: str, top_k: int = 5, decision_id: str = None) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for item in self.shelves:
            for pr in item.get("principles", []):
                s = score(query, pr, item.get("weight", 1.0))
                if s > 0:
                    rec = {
                        "book": item.get("book"),
                        "chapter": pr.get("chapter") or pr.get("derived_from") or "",
                        "principle": pr.get("principle"),
                        "score": s,
                        "principle_id": pr.get("principle_id") or pr.get("id") or pr.get("derived_from"),
                    }
                    results.append(rec)

        # sort and trim
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

        # Emit RAGTrace for audit (best-effort)
        try:
            for r in results:
                try:
                    log_rag_trace(decision_id, r["book"], r.get("chapter", ""), r.get("principle", ""), "applied in debate", r.get("score", 0.0))
                except Exception:
                    pass
        except Exception:
            pass

        return results
"""Simple per-minister retrieval helper.

Provides `retrieve_for_minister` which loads book metadata and returns
the top-N books for a given minister and mode using `MinisterRAGSelector`.
"""
from core.rag.minister_rag_selector import MinisterRAGSelector
from core.knowledge.book_metadata_loader import BookMetadataLoader


def retrieve_for_minister(minister_name, context=None, mode="standard", cap=5, decision_id=None, decay_toggle=False, current_year=None):
    """Return a ranked list of book metadata dicts for the minister.

    Args:
        minister_name: Friendly minister name (e.g., 'Psychology')
        context: Optional retrieval context (currently unused)
        mode: Retrieval mode, e.g., 'war' or 'standard'
        cap: Maximum number of books to return

    Returns:
        List[dict] of book metadata (ranked)
    """
    loader = BookMetadataLoader()
    all_meta = loader.load_all()

    # Convert mapping to list of metadata dicts
    books = list(all_meta.values())

    selector = MinisterRAGSelector()
    ranked = selector.select(minister_name, books, mode)
    top = ranked[:cap]

    # Optional confidence decay based on publication year
    def apply_decay(score, pub_year, toggle):
        try:
            if not toggle or pub_year is None:
                return score
            cy = current_year or __import__('datetime').datetime.utcnow().year
            age = cy - int(pub_year)
            return score * max(0.6, 1 - age * 0.01)
        except Exception:
            return score

    if decay_toggle:
        for b in top:
            try:
                original = float(b.get('score', 0.0))
                py = b.get('publication_year') or b.get('year')
                b['score'] = apply_decay(original, py, True)
            except Exception:
                pass

    # Best-effort: log selected books as RAG traces when a decision_id is provided
    if decision_id:
        try:
            from core.rag.trace import log_rag_trace
            for b in top:
                # Attempt to extract reasonable fields from metadata
                book_title = b.get("title") or b.get("book") or b.get("id")
                chapter = b.get("chapter", "")
                principle = b.get("principle_id") or b.get("principle") or ""
                interp = ""  # minister-specific interpretation left to caller
                score = b.get("score", 0.0)
                log_rag_trace(decision_id, book_title, chapter, principle, interp, score)
        except Exception:
            pass

    return top
