from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class Principle:
    id: str
    text: str
    pattern: str
    application_space: List[str]
    contraindications: List[str]
    source: Dict  # book, chapter, page_range
    shelves: List[str]
    minister_affinity: Dict[str, float]
    timeless: bool
    published_year: int
