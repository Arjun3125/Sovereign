"""Schemas and constants for ingest_v2.

Provides the fixed domain list expected by the prompt set.
"""

DOMAIN_LIST = [
    "grand_strategy",
    "power",
    "optionality",
    "psychology",
    "diplomacy",
    "conflict",
    "truth",
    "risk",
    "timing",
    "data_judgment",
    "operations",
    "technology",
    "adaptation",
    "legitimacy",
    "narrative",
]
"""Schemas and domain list for ingest_v2."""
from typing import List

# Fixed domain list used by domain_classifier
DOMAIN_LIST: List[str] = [
    "power",
    "strategy",
    "diplomacy",
    "economy",
    "timing",
]

# Minimal JSON/YAML schema placeholders (for validation-only)
CHAPTER_SCHEMA = {
    "type": "object",
    "properties": {
        "chapter_id": {"type": "string"},
        "title": {"type": "string"},
        "text": {"type": "string"},
    },
    "required": ["chapter_id", "title", "text"],
}

BOOK_MEMORY_SCHEMA = {
    "type": "object",
}
