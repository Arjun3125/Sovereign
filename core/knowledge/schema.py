from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class KnowledgeChunk:
    book_id: str
    chapter: str
    chapter_title: str
    text: str
    domains: List[str]
    allowed_ministers: List[str]
