from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DoctrineView:
    doctrine_id: str
    derived_from_snapshot: str
    principle_ids: List[str]
    rationale: str
    created_at: str
