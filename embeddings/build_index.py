import os
import requests
import numpy as np
from query_engine.loader import load_book
from .store import save

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embeddings")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


def embed(texts):
    """Embed a list of texts using Ollama embedding model.
    
    Args:
        texts: List of text strings.
        
    Returns:
        Numpy array of embeddings, shape (len(texts), embedding_dim).
    """
    vecs = []
    for t in texts:
        r = requests.post(
            OLLAMA_URL,
            json={"model": EMBED_MODEL, "prompt": t},
            timeout=120
        )
        r.raise_for_status()
        vecs.append(r.json()["embedding"])
    return np.array(vecs, dtype="float32")


def build(book_id: str):
    """Build and save embeddings for a book's chapters.
    
    Args:
        book_id: Book identifier (must be already ingested).
    """
    chapters = load_book(book_id)

    texts = []
    meta = []
    for ch in chapters:
        joined = "\n".join(
            ch.get("principles", [])
            + ch.get("claims", [])
            + ch.get("rules", [])
            + ch.get("warnings", [])
        )
        texts.append(joined)
        meta.append({
            "chapter_index": ch["chapter_index"],
            "chapter_title": ch["chapter_title"]
        })

    vectors = embed(texts)
    save(book_id, vectors, meta)
