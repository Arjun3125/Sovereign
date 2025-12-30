import os
import json
import numpy as np

BASE = "doctrine_storage/embeddings"


def _paths(book_id):
    os.makedirs(BASE, exist_ok=True)
    return (
        os.path.join(BASE, f"{book_id}.npy"),
        os.path.join(BASE, f"{book_id}.meta.json"),
    )


def save(book_id, vectors, meta):
    """Save embedding vectors and metadata for a book.
    
    Args:
        book_id: Book identifier.
        vectors: Numpy array of shape (n_chapters, embedding_dim).
        meta: List of metadata dicts with chapter info.
    """
    vec_path, meta_path = _paths(book_id)
    np.save(vec_path, vectors)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load(book_id):
    """Load embedding vectors and metadata for a book.
    
    Args:
        book_id: Book identifier.
        
    Returns:
        Tuple of (vectors, meta) or raises RuntimeError if not found.
    """
    vec_path, meta_path = _paths(book_id)
    if not (os.path.exists(vec_path) and os.path.exists(meta_path)):
        raise RuntimeError("Embeddings not built")
    vectors = np.load(vec_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return vectors, meta
