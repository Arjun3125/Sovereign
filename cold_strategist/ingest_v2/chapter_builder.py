"""Chapter builder for ingest_v2.
Builds simple chapter objects from raw text.
"""
import re
from typing import List, Dict


def _is_roman(s: str) -> bool:
    return bool(re.match(r"^[IVXLCDM]+$", s.strip().upper()))


def build_chapters(raw_text: str) -> List[Dict]:
    """Return list of chapters: {chapter_id, title, text}.

    Simple heuristic splitter: split on lines that look like chapter headings
    (e.g., 'CHAPTER I', 'I.', or uppercase short lines). Keeps Roman numerals.
    """
    lines = raw_text.splitlines()
    markers = []
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t:
            continue
        # common markers
        if re.match(r'^(CHAPTER|Chapter)\b', t):
            markers.append((i, t))
            continue
        # roman numerals on their own line
        if _is_roman(t.replace('.', '').split()[0]):
            markers.append((i, t))
            continue
        # short uppercase lines
        if t.isupper() and 1 <= len(t.split()) <= 6:
            markers.append((i, t))

    # If no markers found, return the whole book as one chapter
    if not markers:
        return [{"chapter_id": "1", "title": "FULL_TEXT", "text": raw_text}]

    chapters = []
    for idx, (pos, title) in enumerate(markers):
        start = pos
        end = markers[idx + 1][0] if idx + 1 < len(markers) else len(lines)
        chunk = "\n".join(lines[start:end]).strip()
        chap_id = str(idx + 1)
        chapters.append({"chapter_id": chap_id, "title": title.strip(), "text": chunk})

    return chapters
"""Minimal scaffold for ingest v2: chapter building"""
def build_chapters(text: str):
    raise NotImplementedError("chapter builder not implemented")
