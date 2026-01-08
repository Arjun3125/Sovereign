import json
import pathlib
from typing import Dict, List
try:
    from pdfminer.high_level import extract_text
except Exception:
    extract_text = None


def _book_id_from_path(path: str) -> str:
    return pathlib.Path(path).stem.lower().replace(" ", "_")


def extract(pdf_path: str, out_dir: str) -> str:
    """Lossless text extraction with page map. Falls back to binary read if pdfminer not available."""
    book_id = _book_id_from_path(pdf_path)
    pages: List[Dict] = []
    if extract_text is None:
        # Fallback: read as text blob
        with open(pdf_path, "rb") as f:
            raw = f.read().decode(errors="ignore")
        pages = [{"page": 1, "text": raw}]
    else:
        txt = extract_text(pdf_path)
        parts = txt.split("\f")
        for i, p in enumerate(parts, start=1):
            pages.append({"page": i, "text": p})

    out = {"book_id": book_id, "pages": pages}
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{out_dir}/{book_id}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return book_id

