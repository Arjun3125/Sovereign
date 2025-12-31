import json
import pathlib
import hashlib
from typing import Dict, Any


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def persist(book_id: str, *json_paths: str, store: str = "rag_store/books") -> None:
    base = pathlib.Path(store) / book_id
    base.mkdir(parents=True, exist_ok=True)
    for p in json_paths:
        with open(p, "rb") as f:
            b = f.read()
        h = _sha256_bytes(b)
        out = base / pathlib.Path(p).name
        with open(out, "wb") as w:
            w.write(b)
        with open(str(out) + ".sha256", "w", encoding='utf-8') as s:
            s.write(h)

