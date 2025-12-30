import json
import os
from typing import List, Dict

BASE = "doctrine_storage/books"


def load_book(book_id: str) -> List[Dict]:
    path = os.path.join(BASE, book_id, "doctrine_chapters")
    if not os.path.exists(path):
        raise RuntimeError("Book not ingested")

    chapters = []
    for f in sorted(os.listdir(path)):
        if f.endswith(".json"):
            with open(os.path.join(path, f), "r", encoding="utf-8") as fh:
                chapters.append(json.load(fh))
    return chapters
