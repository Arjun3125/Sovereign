from pathlib import Path
import yaml


def load_book(book_dir):
    book_dir = Path(book_dir)
    meta = yaml.safe_load((book_dir / "meta.yaml").read_text())
    raw = (book_dir / "raw.txt").read_text(encoding="utf-8")

    return {
        "book_id": meta["book_id"],
        "meta": meta,
        "raw_text": raw
    }
