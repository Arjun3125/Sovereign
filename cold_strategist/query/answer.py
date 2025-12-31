from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class HardenedAnswer:
    answer: str
    confidence: float
    authority: str
    sources: Dict[str, Any]
