from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class SourceRef:
    book: str
    principle: str
    location: Optional[str]  # chapter / section
    confidence: float        # 0–1 usefulness score

@dataclass
class KnowledgeChunk:
    text: str                    # distilled principle (not quote)
    domain: str                  # psychology, power, conflict, etc
    source: SourceRef
    embedding: Optional[list] = None
