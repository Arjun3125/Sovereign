import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import numpy as np
except Exception:
    np = None

try:
    # faiss requires numpy
    if np is not None:
        import faiss
        _FAISS = True
    else:
        faiss = None
        _FAISS = False
except Exception:
    faiss = None
    _FAISS = False


def _deterministic_embed(text: str, dim: int = 128):
    """Deterministic pseudo-embedding based on SHA256 bytes.

    Not a semantic embedder, but deterministic and useful as a fallback.
    """
    h = hashlib.sha256(text.encode('utf-8')).digest()
    # expand bytes to required dim by repeated hashing
    vals = []
    i = 0
    src = h
    while i < dim:
        for b in src:
            if i >= dim:
                break
            vals.append((b / 255.0) * 2.0 - 1.0)
            i += 1
        src = hashlib.sha256(src).digest()

    # normalize
    if np is not None:
        arr = np.array(vals, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr
    else:
        # pure-Python normalize
        import math
        norm = math.sqrt(sum(v * v for v in vals))
        if norm > 0:
            vals = [v / norm for v in vals]
        return vals


class VectorStore:
    def __init__(self, dim: int = 128, path: Optional[Path] = None, use_faiss: bool = True):
        self.dim = dim
        self.vectors: List[np.ndarray] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.path = Path(path) if path is not None else None
        self._index = None
        self.use_faiss = use_faiss and _FAISS

    def add(self, text: str, metadata: Dict[str, Any]):
        vec = _deterministic_embed(text, self.dim)
        self.vectors.append(vec)
        meta = dict(metadata or {})
        meta["text"] = text
        self.metadatas.append(meta)

    def build(self):
        if not self.vectors:
            if np is not None:
                self._matrix = np.empty((0, self.dim), dtype=np.float32)
            else:
                self._matrix = []
            return

        if np is not None:
            self._matrix = np.vstack(self.vectors).astype(np.float32)
        else:
            # vectors are lists
            self._matrix = [list(v) for v in self.vectors]

        if self.use_faiss and np is not None:
            self._index = faiss.IndexFlatIP(self.dim)
            # ensure vectors are normalized for inner-product as cosine
            norms = np.linalg.norm(self._matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self._matrix = self._matrix / norms
            self._index.add(self._matrix)

    def persist(self, path: Path):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        # save metadata
        with open(p / "metadatas.json", "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f, ensure_ascii=False, indent=2)
        # save vectors
        if np is not None:
            np.save(p / "vectors.npy", self._matrix)
        else:
            # persist as json list
            with open(p / "vectors.json", "w", encoding="utf-8") as f:
                json.dump(self._matrix, f, ensure_ascii=False)

        # if faiss index present, save it too
        if self.use_faiss and self._index is not None:
            faiss.write_index(self._index, str(p / "index.faiss"))

    @classmethod
    def load(cls, path: Path):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Index path not found: {p}")
        vs = cls(path=p)
        with open(p / "metadatas.json", "r", encoding="utf-8") as f:
            vs.metadatas = json.load(f)
        if (p / "vectors.npy").exists() and np is not None:
            mat = np.load(p / "vectors.npy")
            vs._matrix = mat.astype(np.float32)
        else:
            # fallback read json vectors
            try:
                vs._matrix = json.loads((p / "vectors.json").read_text(encoding='utf-8'))
            except Exception:
                vs._matrix = []
        vs.dim = vs._matrix.shape[1]
        if _FAISS and (p / "index.faiss").exists():
            vs._index = faiss.read_index(str(p / "index.faiss"))
        return vs

    def _search_numpy(self, qvec, top_k: int = 5):
        if getattr(self, "_matrix", None) is None:
            return []
        if np is not None and hasattr(self._matrix, 'shape') and self._matrix.size == 0:
            return []
        # cosine similarity (vectors normalized)
        if np is not None:
            qnorm = qvec / (np.linalg.norm(qvec) + 1e-12)
            mat = self._matrix
            if mat.shape[1] != qnorm.shape[0]:
                return []
            sims = mat.dot(qnorm)
            idx = np.argsort(-sims)[:top_k]
            return [(int(i), float(sims[i])) for i in idx]

        # pure-Python fallback
        import math
        qnorm = qvec
        qnorm_sum = math.sqrt(sum(v * v for v in qnorm))
        if qnorm_sum == 0:
            return []
        qnorm = [v / qnorm_sum for v in qnorm]
        sims = []
        for i, row in enumerate(self._matrix):
            # row is list
            dot = sum(a * b for a, b in zip(row, qnorm))
            sims.append((i, dot))
        sims.sort(key=lambda x: x[1], reverse=True)
        return [(int(i), float(s)) for i, s in sims[:top_k]]

    def search(self, query: str, top_k: int = 5):
        qvec = _deterministic_embed(query, self.dim)
        if self.use_faiss and self._index is not None:
            # ensure query normalized (IndexFlatIP expects normalized for cosine)
            q = qvec.reshape(1, -1).astype(np.float32)
            q /= (np.linalg.norm(q) + 1e-12)
            D, I = self._index.search(q, top_k)
            results = []
            for score, idx in zip(D[0].tolist(), I[0].tolist()):
                if idx < 0:
                    continue
                meta = self.metadatas[idx]
                results.append({"text": meta.get("text"), "meta": meta, "similarity": float(score)})
            return results

        hits = self._search_numpy(qvec, top_k)
        results = []
        for idx, sim in hits:
            meta = self.metadatas[idx]
            results.append({"text": meta.get("text"), "meta": meta, "similarity": float(sim)})
        return results
