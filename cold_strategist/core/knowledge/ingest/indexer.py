from typing import List, Dict, Any
from utils.hash import chunk_hash


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
    # Build an in-memory set of existing hashes once per run
    existing_hashes = set()
    try:
        # VectorIndex implementations keep payloads in a list named `payloads`
        for p in getattr(index, "payloads", []):
            h = p.get("hash") if isinstance(p, dict) else None
            if h:
                existing_hashes.add(h)
    except Exception:
        existing_hashes = set()

    inserted = 0
    skipped = 0

    for c in chunks:
        book_id = c.get("book_id", "")
        text = c.get("text", "")

        h = chunk_hash(book_id, text, version="v1")
        if h in existing_hashes:
            skipped += 1
            continue

        embedding = embed_fn(text)

        # Build immutable payload for retrieval filtering
        payload = {
            "book_id": book_id,
            "chapter": c.get("chapter"),
            "text": text,
            "type": c.get("type", "principle"),
            "domains": c.get("domains", []),
            "allowed_ministers": c.get("allowed_ministers", []),
            "source": c.get("source", {}),
            "hash": h,
        }

        # Add to index (wrapper handles vector + payload)
        index.add_with_payload(embedding, payload)
        inserted += 1

    # Simple log for health signal
    try:
        print(f"[INDEX] Chunks inserted: {inserted}, skipped (already embedded): {skipped}")
    except Exception:
        pass
