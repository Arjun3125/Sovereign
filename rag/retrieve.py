from typing import List


def retrieve_principles(index, query: str, embed_fn, domain: str = None, k: int = 5):
    q_emb = embed_fn(query)
    results = index.search(q_emb, k=k)

    if domain:
        results = [r for r in results if r.domain == domain]

    return results
