import os
import requests
from typing import List, Dict

USE_EMB = os.getenv("USE_EMBEDDINGS", "0") == "1"
OLLAMA_EMB_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


def _embed_query(q):
    """Embed a query using Ollama embedding model.
    
    Args:
        q: Query string.
        
    Returns:
        Embedding vector.
    """
    r = requests.post(
        OLLAMA_EMB_URL,
        json={"model": EMBED_MODEL, "prompt": q},
        timeout=60
    )
    r.raise_for_status()
    return r.json()["embedding"]


def retrieve(question: str, chapters: List[Dict], limit: int = 5, book_id: str = None) -> List[Dict]:
    """Retrieve relevant chapters using symbolic or embedding-based retrieval.
    
    Args:
        question: User question.
        chapters: List of chapter dicts.
        limit: Max chapters to return.
        book_id: Book identifier (required for embedding retrieval).
        
    Returns:
        List of relevant chapter dicts.
    """
    if not USE_EMB:
        # symbolic fallback (existing logic)
        q = question.lower()
        scored = []

        for ch in chapters:
            text = " ".join(
                ch.get("principles", [])
                + ch.get("claims", [])
                + ch.get("rules", [])
                + ch.get("warnings", [])
            ).lower()

            score = sum(1 for word in q.split() if word in text)
            if score > 0:
                scored.append((score, ch))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ch for _, ch in scored[:limit]]

    # embeddings path
    if not book_id:
        raise ValueError("book_id required for embedding retrieval")
    
    from embeddings.retriever import retrieve as emb_retrieve
    
    qv = _embed_query(question)
    hits = emb_retrieve(book_id, qv, k=limit)
    idx = {h["chapter_index"] for h in hits}
    return [ch for ch in chapters if ch["chapter_index"] in idx]
