from typing import List, Dict, Any


def index_chunks(chunks: List[Dict[str, Any]], embed_fn, index) -> None:
    """
    Index chunks with embeddings and metadata payloads.
    
    Each chunk is stored with:
    - vector: embedding of raw text
    - payload: metadata (book, chapter, domains, permissions, source)
    
    Args:
        chunks: List of enriched chunk dicts
        embed_fn: Embedding function
        index: VectorIndex instance
    """
    for c in chunks:
        embedding = embed_fn(c["text"])
        
        # Build immutable payload for retrieval filtering
        payload = {
            "book_id": c.get("book_id"),
            "chapter": c.get("chapter"),
            "text": c.get("text"),
            "type": c.get("type", "principle"),
            "domains": c.get("domains", []),
            "allowed_ministers": c.get("allowed_ministers", []),
            "source": c.get("source", {})
        }
        
        # Add to index (wrapper handles vector + payload)
        index.add_with_payload(embedding, payload)
