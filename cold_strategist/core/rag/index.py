import json
import pathlib
from typing import Dict, Any


class RAGIndex:
    def __init__(self, store: str = "rag_store/books"):
        self.store = pathlib.Path(store)
        self.books: Dict[str, Dict[str, Any]] = {}

    def load(self):
        if not self.store.exists():
            return self
        for book_dir in self.store.iterdir():
            if not book_dir.is_dir():
                continue
            book_id = book_dir.name
            try:
                structural = json.load(open(book_dir / "structural.json", "r", encoding="utf-8"))
            except Exception:
                structural = {}
            try:
                semantic = json.load(open(book_dir / "semantic.json", "r", encoding="utf-8"))
            except Exception:
                semantic = {}
            try:
                principles = json.load(open(book_dir / "principles.json", "r", encoding="utf-8"))
            except Exception:
                principles = {}
            try:
                affinity = json.load(open(book_dir / "affinity.json", "r", encoding="utf-8"))
            except Exception:
                affinity = {}

            self.books[book_id] = {
                "structural": structural,
                "semantic": semantic,
                "principles": principles,
                "affinity": affinity,
            }

        return self
