import json
import os
from .storage import chapter_exists


def load_committed_chapters(book_id):
    base = f"doctrine_storage/books/{book_id}/doctrine_chapters"
    if not os.path.exists(base):
        return set()

    committed = set()
    for f in os.listdir(base):
        if f.endswith(".json"):
            try:
                committed.add(int(f.replace(".json", "")))
            except Exception:
                continue
    return committed


def should_skip(book_id, chapter):
    if not chapter_exists(book_id, chapter.index):
        return False

    path = (
        f"doctrine_storage/books/{book_id}/doctrine_chapters/"
        f"{chapter.index:02}.json"
    )

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    stored_hash = data.get("source_hash")
    if stored_hash != chapter.hash:
        raise RuntimeError(
            f"Hash mismatch on chapter {chapter.index}. "
            f"Source changed — new book_id required."
        )

    return True
