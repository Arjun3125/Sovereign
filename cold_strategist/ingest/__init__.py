"""
Unified Ingestion Module

Consolidates all ingestion pipelines (Phase-1/Phase-2 compiler, alternative pipeline, validation/audit).
Provides clean import surface for ingestion functionality.

Submodules:
  - core: Phase-1 & Phase-2 LLM-based ingestion pipeline
  - v1: Alternative PDF-to-doctrine ingestion pipeline
  - audit: Quality assurance, conflict detection, audit reporting
  - storage: Doctrine storage (books data)
  - scripts: Entry point scripts (ingest_all_books, post_ingest_validation, etc.)
"""

# Core pipeline (Phase-1 & Phase-2)
from .core.ingest_v2 import ingest_v2
from .core.phase1_structure import phase1_structure
from .core.phase2_doctrine import phase2_doctrine
from .core.llm_client import call_llm, LLMError
from .core.validators import validate_phase1, validate_phase2, ValidationError
from .core.progress import Progress

# Alternative pipeline (v1)
from .v1.ingest import ingest_book
from .v1.pdf_reader import extract_pages
from .v1.phase2_extract import extract_doctrine
from .v1.validator import validate

# Note: Audit functions available via explicit import if needed:
# from .audit.detect import detect_conflicts
# from .audit.normalize import normalize
# from .audit.pairwise import is_direct_contradiction
# from .audit.report import format_report

__all__ = [
    # Core pipeline
    "ingest_v2",
    "phase1_structure",
    "phase2_doctrine",
    "call_llm",
    "LLMError",
    "validate_phase1",
    "validate_phase2",
    "ValidationError",
    "Progress",
    # Alternative pipeline
    "ingest_book",
    "extract_pages",
    "extract_doctrine",
    "validate",
]
