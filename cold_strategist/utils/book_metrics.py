import json
from pathlib import Path
from collections import defaultdict

BOOK_METRICS = Path("cold_strategist/state/book_progress.json")

def init_book(book_id: str, total_chunks: int):
    data = {}
    if BOOK_METRICS.exists():
        try:
            data = json.loads(BOOK_METRICS.read_text())
        except Exception:
            data = {}

    if book_id not in data:
        data[book_id] = {
            "total_chunks": total_chunks,
            "completed_chunks": 0,
            "skipped_chunks": 0
        }

    BOOK_METRICS.parent.mkdir(parents=True, exist_ok=True)
    BOOK_METRICS.write_text(json.dumps(data, indent=2))


def update_book(book_id: str, completed=0, skipped=0):
    if not BOOK_METRICS.exists():
        return

    try:
        data = json.loads(BOOK_METRICS.read_text())
    except Exception:
        return

    if book_id not in data:
        return

    data[book_id]["completed_chunks"] = data[book_id].get("completed_chunks", 0) + completed
    data[book_id]["skipped_chunks"] = data[book_id].get("skipped_chunks", 0) + skipped

    BOOK_METRICS.write_text(json.dumps(data, indent=2))
