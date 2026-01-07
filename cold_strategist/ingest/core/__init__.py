"""
Phase-1 & Phase-2 LLM-based ingestion pipeline.

Two-pass doctrine compiler:
  - Phase-1: Extract chapters from raw text using LLM
  - Phase-2: Extract doctrine from each chapter using LLM
  - Resume-safe progress tracking
  - Schema-hardened validation
"""

from .ingest_v2 import ingest_v2
from .phase1_structure import phase1_structure
from .phase2_doctrine import phase2_doctrine
from .llm_client import call_llm, LLMError
from .validators import validate_phase1, validate_phase2, ValidationError
from .progress import Progress

__all__ = [
    "ingest_v2",
    "phase1_structure",
    "phase2_doctrine",
    "call_llm",
    "LLMError",
    "validate_phase1",
    "validate_phase2",
    "ValidationError",
    "Progress",
]
