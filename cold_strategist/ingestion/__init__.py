"""Doctrine ingestion package (compiler-like, deterministic, read-only artifacts).

This package contains tools to extract chapters from PDFs, process them
via a pluggable LLM client, validate and persist immutable doctrine
artifacts under `doctrine_storage/books/`.
"""

__all__ = [
    "ingest",
    "pdf_reader",
    "chapter_detector",
    "chapter_model",
    "llm_client",
    "chapter_processor",
    "assembler",
    "storage",
    "validator",
]
