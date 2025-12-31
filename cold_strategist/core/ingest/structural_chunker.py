import re
import json
import pathlib
from typing import Dict, Any, List

CHAPTER_RX = re.compile(r"^\s*(chapter|book|part)\b", re.I)


def chunk_structure(raw: Dict[str, Any]) -> Dict[str, Any]:
    pages = raw.get("pages", [])
    text = "\n".join(p.get("text", "") for p in pages)

    # naive chapter/section split: split on lines that look like headings
    lines = [l for l in text.splitlines()]

    sections: List[Dict] = []
    current = {"chapter": "front_matter", "text": "", "pages": []}

    for p in pages:
        page_text = p.get("text", "")
        first_line = page_text.splitlines()[0] if page_text.strip() else ""
        if CHAPTER_RX.search(first_line[:120]):
            if current["text"].strip():
                sections.append(current)
            current = {"chapter": first_line.strip()[:80], "text": "", "pages": []}
        current["text"] += page_text + "\n"
        current["pages"].append(p.get("page"))

    if current["text"].strip():
        sections.append(current)

    out = {"book_id": raw.get("book_id"), "sections": sections}
    pathlib.Path.cwd()
    return out
