import json
from ..embedding.domain_vector_manager import DomainVectorStore
from ..models.embedding_client import embed_text
from ..config.domains import DOMAIN_INDEX
from ..config.ministers import MINISTER_DOMAINS

def retrieve_for_minister(minister: str, query: str, top_k: int = 3) -> list:
    """Retrieve doctrines only from minister's domains."""
    vector = embed_text(query)
    results = []

    for domain in MINISTER_DOMAINS[minister]:
        store = DomainVectorStore(DOMAIN_INDEX[domain])
        hits = store.search(vector, top_k=top_k)
        for score, meta in hits:
            results.append({
                "score": score,
                "doctrine_id": meta["doctrine_id"],
                "confidence": meta["confidence"],
                "domain": domain,
                "source": meta.get("source", {})
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
