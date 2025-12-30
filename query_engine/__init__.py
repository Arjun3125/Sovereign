"""Query engine: read-only access to compiled doctrine and a simple symbolic retriever.

This package provides a conservative, auditable query path that only
reads from `doctrine_storage/books/*/doctrine_chapters/*.json` and never
performs any writes or ingestion calls.
"""

from .ask import ask
from .loader import load_book
from .retriever import retrieve
from .prompt import build_prompt
from .synthesize import synthesize

__all__ = ["ask", "load_book", "retrieve", "build_prompt", "synthesize"]
