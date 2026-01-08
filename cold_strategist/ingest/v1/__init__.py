"""Alternative PDF-to-doctrine ingestion pipeline.

Tools to extract chapters from PDFs, process them via LLM,
validate and persist doctrine artifacts.
"""

from .ingest import ingest_book
from .pdf_reader import extract_pages
from .phase2_extract import extract_doctrine
from .validator import validate

__all__ = [
    "ingest_book",
    "extract_pages",
    "extract_doctrine",
    "validate",
]
