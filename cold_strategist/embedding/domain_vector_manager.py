import faiss
import numpy as np
import json
from pathlib import Path

DIMENSION = 768  # nomic-embed-text

class DomainVectorStore:
    """FAISS index per domain."""
    
    def __init__(self, path: str):
        self.path = Path(path)
        if self.path.exists():
            self.index = faiss.read_index(str(self.path))
        else:
            self.index = faiss.IndexFlatIP(DIMENSION)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> list:
        """Load metadata JSON if exists."""
        meta_path = self.path.with_suffix(".meta.json")
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return []

    def add(self, vector: list, meta: dict):
        """Add vector + metadata."""
        vec_array = np.array([vector], dtype=np.float32)
        self.index.add(vec_array)
        self.metadata.append(meta)

    def save(self):
        """Persist index and metadata."""
        self.path.parent.mkdir(exist_ok=True)
        faiss.write_index(self.index, str(self.path))
        meta_path = self.path.with_suffix(".meta.json")
        meta_path.write_text(json.dumps(self.metadata, indent=2))

    def search(self, vector: list, top_k: int = 3) -> list:
        """Search and return (score, metadata) tuples."""
        if not self.metadata:
            return []
        vec_array = np.array([vector], dtype=np.float32)
        k = min(top_k, len(self.metadata))
        scores, ids = self.index.search(vec_array, k)
        return [
            (float(scores[0][i]), self.metadata[ids[0][i]])
            for i in range(len(ids[0]))
        ]
