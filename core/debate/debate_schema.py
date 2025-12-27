"""
Debate Schema - Verdict and Objection Data Structures (LOCKED)

Canonical forms for minister statements during debate.
No philosophy. No ethics. Only analysis and warnings.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ObjectionType(str, Enum):
    """Valid objection categories."""
    RISK = "risk"
    ILLUSION = "illusion"
    TIMING = "timing"
    IRREVERSIBILITY = "irreversibility"
    POWER_LEAK = "power_leak"
    FEASIBILITY = "feasibility"


class VerdictType(str, Enum):
    """High-level verdict classification."""
    VIABLE = "viable"
    VIABLE_BUT_DESTRUCTIVE = "viable_but_destructive"
    NON_VIABLE = "non_viable"
    CONTINGENT = "contingent"


@dataclass
class MinisterVerdict:
    """
    Independent verdict from a single minister.
    
    Submitted without knowledge of other verdicts.
    Includes position, warning, confidence.
    """
    
    minister_name: str
    position: str                          # What to do (specific recommendation)
    warning: str                           # What fails or risks
    confidence: float                      # 0.0-1.0 confidence in position
    verdict_type: VerdictType = VerdictType.VIABLE
    evidence: List[str] = field(default_factory=list)  # Justifying evidence
    conditions: List[str] = field(default_factory=list)  # Conditions for viability
    
    def is_viable(self) -> bool:
        """Check if this minister thinks the position is viable."""
        return self.verdict_type in [
            VerdictType.VIABLE,
            VerdictType.VIABLE_BUT_DESTRUCTIVE,
            VerdictType.CONTINGENT
        ]


@dataclass
class Objection:
    """
    Formal objection from one minister to another.
    
    Submitted after Phase 1 (independent positions).
    Targets specific verdicts with specific reasons.
    """
    
    objector: str
    target_minister: str
    objection_type: ObjectionType
    statement: str                         # Why this verdict is wrong/incomplete
    severity: str = "medium"               # low / medium / high
    counter_position: Optional[str] = None  # Alternative if applicable
    
    def __hash__(self):
        """Make objection hashable for deduplication."""
        return hash((self.objector, self.target_minister, self.objection_type))


@dataclass
class Concession:
    """
    When a minister acknowledges partial validity of an objection.
    
    Not full agreement, but partial correction.
    """
    
    minister_name: str
    concedes_to: str
    original_claim: str
    revised_claim: Optional[str]
    reason: str


@dataclass
class DebateRound:
    """
    Complete record of one phase of the debate.
    
    Tracks verdicts, objections, concessions, and contradictions found.
    """
    
    phase: int                             # Phase number (1, 2, etc.)
    verdicts: List[MinisterVerdict] = field(default_factory=list)
    objections: List[Objection] = field(default_factory=list)
    concessions: List[Concession] = field(default_factory=list)
    
    def verdicts_by_minister(self) -> dict:
        """Get verdicts indexed by minister name."""
        return {v.minister_name: v for v in self.verdicts}
    
    def objections_to_minister(self, minister_name: str) -> List[Objection]:
        """Get all objections targeting a specific minister."""
        return [o for o in self.objections if o.target_minister == minister_name]
