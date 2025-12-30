from dataclasses import dataclass
from typing import List, Optional, Set, Literal


RetrievalStatus = Literal["RESULTS", "SILENCE", "ERROR"]


@dataclass(frozen=True)
class RetrievedItem:
    chunk: "KnowledgeChunk"
    score: float


@dataclass(frozen=True)
class RetrievalTrace:
    query_text: str
    embedding_model: Optional[str]
    embedding_dim: Optional[int]
    min_score: float
    domain_filter: Optional[Set[str]]
    candidates_total: int
    candidates_after_filter: int
    returned_count: int
    decision_reason: str


@dataclass(frozen=True)
class RetrievalResult:
    status: RetrievalStatus
    items: List[RetrievedItem]
    trace: RetrievalTrace
