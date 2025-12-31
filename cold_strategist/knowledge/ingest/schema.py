"""Minimal schema definitions for persisted knowledge artifacts."""

BOOK_SCHEMA = {
    "book_id": str,
    "title": str,
    "authors": list,
}

SECTION_SCHEMA = {
    "section_id": str,
    "book_id": str,
    "chapter": str,
    "text": str,
}
