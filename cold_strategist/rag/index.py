from typing import Callable, List, Dict, Any
import math


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class VectorIndex:
    def __init__(self, embed_fn: Callable[[str], List[float]]):
        self.embed_fn = embed_fn
        self.vectors: List[List[float]] = []
        self.payloads: List[Dict[str, Any]] = []

    def add(self, chunk):
        """Add a chunk (legacy interface)."""
        chunk.embedding = self.embed_fn(chunk.text)
        self.vectors.append(chunk.embedding)
        self.payloads.append({})

    def add_with_payload(self, vector: List[float], payload: Dict[str, Any]) -> None:
        """Add a vector with metadata payload."""
        self.vectors.append(vector)
        self.payloads.append(payload)

    def search(self, query_embedding, k=5) -> List[Dict[str, Any]]:
        """Search and return payloads."""
        scores = [
            (i, cosine_similarity(query_embedding, v))
            for i, v in enumerate(self.vectors)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [self.payloads[i] for i, _ in scores[:k] if i < len(self.payloads)]
