"""Simple YAML schema validator for ingest_v2 book artifacts.

This validator enforces the minimal shape used by downstream systems:

- top-level: `book_id`, `title`, `authors` (opt), `chapters` (list)
- each chapter: `chapter_id`, `title`, `domains` (list), `memory` (list of dicts)

The goal is conservative validation before writing the canonical YAML.
"""
from typing import Dict, Any, List


class ValidationError(Exception):
    pass


def _ensure_list(x, name: str):
    if not isinstance(x, list):
        raise ValidationError(f"{name} must be a list")


def validate_book(book: Dict[str, Any]) -> bool:
    if not isinstance(book, dict):
        raise ValidationError("book must be a dict")
    if "book_id" not in book or not book["book_id"]:
        raise ValidationError("missing book_id")
    if "title" not in book or not book["title"]:
        raise ValidationError("missing title")
    chapters = book.get("chapters")
    if chapters is None:
        raise ValidationError("missing chapters list")
    _ensure_list(chapters, "chapters")

    for ch in chapters:
        if not isinstance(ch, dict):
            raise ValidationError("each chapter must be a dict")
        if "chapter_id" not in ch or not ch["chapter_id"]:
            raise ValidationError("chapter missing chapter_id")
        if "title" not in ch:
            raise ValidationError("chapter missing title")
        domains = ch.get("domains", [])
        _ensure_list(domains, "chapter.domains")
        # memory should be a list of objects with domain + memory_items
        memory = ch.get("memory", [])
        _ensure_list(memory, "chapter.memory")
        for m in memory:
            if not isinstance(m, dict):
                raise ValidationError("memory items must be dicts")
            if "domain" not in m:
                raise ValidationError("memory item missing domain")
            if "memory_items" not in m:
                raise ValidationError("memory item missing memory_items")
            _ensure_list(m["memory_items"], "memory_item.memory_items")

    return True
