import os
import json
import hashlib
import uuid
from typing import Any


def book_id_from_path(path: str) -> str:
    name = os.path.splitext(os.path.basename(path))[0]
    return name.replace(" ", "_").lower()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def deterministic_id(namespace: str, name: str) -> str:
    ns = uuid.uuid5(uuid.NAMESPACE_URL, namespace)
    return str(uuid.uuid5(ns, name))


def write_json(path: str, data: Any, overwrite: bool = False) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and not overwrite:
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
