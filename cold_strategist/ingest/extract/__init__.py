"""PDF/Text extractors package (canonical location).

This package exposes extractor implementations under
`cold_strategist.ingest.extract`.
"""

from .pdf import *

__all__ = ["extract_pdf"]
