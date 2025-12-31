from typing import List, Optional, Callable


def retrieve_principles(
    index,
    query: str,
    embed_fn: Callable[[str], List[float]],
    domain: Optional[str] = None,
    k: int = 5,
    min_score: float = 0.0,
):
    try:
        q_emb = embed_fn(query)
    except Exception as e:
        raise RuntimeError(f"Embedding failure: {e}")

    if not q_emb:
        raise RuntimeError("Embedding returned empty vector")

    filter_fn = (lambda p: p.get("domain") == domain) if domain else None

    results_with_scores = index.search(q_emb, k=k, return_scores=True, min_score=min_score, filter_fn=filter_fn)
    return results_with_scores
