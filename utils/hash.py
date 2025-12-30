import hashlib
from typing import Optional


def stable_hash(content: str, namespace: Optional[str] = None, version: str = "v1", algo: str = "sha256") -> str:
    """Return a deterministic hex digest incorporating namespace and version.

    The namespace parameter provides domain separation (e.g. book id,
    doctrine id) so different domains do not collide even on identical
    content. The returned value is the raw hex digest by default to
    preserve backward compatibility with existing callers.
    """
    if algo != "sha256":
        raise ValueError("Only sha256 is supported")

    prefix = f"{namespace}::" if namespace else ""
    payload = f"{prefix}{version}::{content}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def chunk_hash(book_id: str, chunk_text: str, version: str = "v1") -> str:
    """Compatibility wrapper that namespaces chunk hashes by `book_id`.

    Returns the raw hex digest (same shape as historically used).
    """
    return stable_hash(chunk_text, namespace=book_id, version=version)
