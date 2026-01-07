"""
Ingestion v2: Two-Pass Doctrine Compiler

Phase-1: Whole book → canonical chapters (LLM)
Phase-2: Each chapter → doctrine (15-domain extraction, LLM)

Resume-safe, progress-tracked, schema-hardened.
"""

from .ingest_v2 import ingest_v2

__all__ = ["ingest_v2"]
