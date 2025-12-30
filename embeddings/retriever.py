import numpy as np
from .store import load


def cosine(a, b):
    """Compute cosine similarity between two vectors.
    
    Args:
        a: First vector.
        b: Second vector.
        
    Returns:
        Cosine similarity score.
    """
    return (a @ b) / ((np.linalg.norm(a) + 1e-8) * (np.linalg.norm(b) + 1e-8))


def retrieve(book_id: str, query_vec, k=5):
    """Retrieve top-k chapters by embedding similarity.
    
    Args:
        book_id: Book identifier.
        query_vec: Query embedding vector.
        k: Number of results to return.
        
    Returns:
        List of metadata dicts for top-k chapters.
    """
    vectors, meta = load(book_id)
    scores = [(i, cosine(v, query_vec)) for i, v in enumerate(vectors)]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [meta[i] for i, _ in scores[:k]]
