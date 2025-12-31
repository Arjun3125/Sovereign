import os
import yaml
import hashlib
from typing import List, Dict


def _deterministic_id(book_id: str, chapter_title: str, text: str) -> str:
    h = hashlib.sha1()
    h.update(f"{book_id}|{chapter_title}|{text}".encode("utf-8"))
    return h.hexdigest()


def extract_principles(chapter_text: str, book_meta: Dict) -> List[Dict]:
    """Deterministic, schema-first principle extractor (LLM hooks optional).

    This is a placeholder deterministic extractor returning one example principle
    for demonstration. In production this would call a deterministic LLM pipeline
    (or a rule-based extractor) and write structured output.
    """
    # Deterministic example: take first sentence as principle text
    first_line = chapter_text.strip().split(".\n")[0].strip()

    principle = {
        "id": _deterministic_id(book_meta.get("book_id", ""), book_meta.get("sample_chapter", ""), first_line),
        "text": first_line or "(extracted principle)",
        "pattern": "-",
        "application_space": book_meta.get("application_space", book_meta.get("shelves", [])),
        "contraindications": book_meta.get("contraindications", []),
        "source": {
            "book": book_meta.get("title"),
            "chapter": book_meta.get("sample_chapter", "") ,
            "page_range": book_meta.get("sample_page_range", "")
        },
        "shelves": book_meta.get("shelves", []),
        "minister_affinity": book_meta.get("affinity", {}),
        "timeless": bool(book_meta.get("published_year")),
        "published_year": book_meta.get("published_year", 0),
    }

    return [principle]


def write_principles_for_book(book_id: str, principles: List[Dict], principles_dir: str = None):
    if principles_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        principles_dir = os.path.join(project_root, "books", "principles")

    os.makedirs(principles_dir, exist_ok=True)
    filepath = os.path.join(principles_dir, f"{book_id}.yaml")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(principles, f, sort_keys=False, allow_unicode=True)
    except Exception:
        # Fail silently to avoid blocking ingestion pipeline in this simple helper
        pass
