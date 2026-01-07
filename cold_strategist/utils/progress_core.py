import json
from pathlib import Path

PROGRESS_FILE = Path("cold_strategist/state/ingest_progress.jsonl")


def record_progress(book_id: str, chunk_hash: str) -> None:
    """Record a chunk as successfully processed (append-only ledger).

    This is presentation-agnostic core logic used by both CLI and
    other orchestrators.
    """
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"book_id": book_id, "hash": chunk_hash}) + "\n")


def load_progress_hashes(book_id: str) -> set:
    """Load all successfully-processed hashes for a book.

    Returns empty set if progress file doesn't exist yet.
    """
    if not PROGRESS_FILE.exists():
        return set()

    seen = set()
    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("book_id") == book_id:
                    seen.add(obj.get("hash"))
            except json.JSONDecodeError:
                continue
    return seen
