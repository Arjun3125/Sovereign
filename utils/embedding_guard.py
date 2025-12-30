"""GPU-safe embedding with semaphore guard.

Prevents concurrent embedding overload on RTX 4060 (8GB VRAM).

Safe limits:
  - 2 concurrent embeddings (standard)
  - 3 max (not recommended)

Reasoning (LLM) stays single-threaded.
"""

from threading import Semaphore
from typing import List, Set
from enum import Enum
import re

# RTX 4060 safe concurrent embeddings
GPU_SEMAPHORE = Semaphore(2)


class EmbedDecision(Enum):
    NEW = "new"
    SKIPPED = "skipped"
    CONFLICT = "conflict"


_HASH_SCHEMA_RE = re.compile(r"^v\d+:sha256:[0-9a-f]{64}$")


def validate_hash_schema(h: str) -> bool:
    """Validate that a hash follows the canonical schema `v<digit>:sha256:<64hex>`.

    This enforces an explicit version and algorithm so that changes to
    the underlying hashing don't silently change semantics.
    """
    return bool(_HASH_SCHEMA_RE.match(h))


def decide_embedding(hash_str: str, existing_hashes: Set[str]) -> EmbedDecision:
    """Decide whether to embed based on canonical hash and seen set.

    Args:
        hash_str: Canonical hash string (validated)
        existing_hashes: Set of seen canonical hash strings

    Returns:
        EmbedDecision
    """
    if not validate_hash_schema(hash_str):
        raise ValueError("Invalid hash schema, expected v<digit>:sha256:<64hex>")

    if hash_str in existing_hashes:
        return EmbedDecision.SKIPPED

    # For now there is no deeper conflict detection; a future check
    # could compare digest collisions across namespaces.
    return EmbedDecision.NEW


def embed_with_guard(text: str) -> List[float]:
    """Generate embedding with GPU semaphore protection.

    Acquires semaphore before calling Ollama embeddings. Keeps the
    original behavior but does not mix decision logic here.
    """
    from ollama import embeddings

    with GPU_SEMAPHORE:
        response = embeddings(model="nomic-embed-text", prompt=text)
        return response["embedding"]
