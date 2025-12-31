"""PDF reader for ingest_v2 (minimal).
Function: extract_text(pdf_path) -> str
"""
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    # Minimal implementation: if a .txt sibling exists, use it, otherwise return placeholder.
    txt_path = p.with_suffix('.txt')
    if txt_path.exists():
        return txt_path.read_text(encoding='utf-8')

    # No PDF parsing dependency here — return a small placeholder indicating the file.
    return f"[PDF TEXT PLACEHOLDER for {p.name}]\n\nPlease replace pdf_reader.extract_text with a real PDF parser."
