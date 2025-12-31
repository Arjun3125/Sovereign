"""
Context Schema - Canonical Decision Context Definition (LOCKED)

Defines the structure of raw human input → structured decision context.
Deterministic. No philosophy. No ministers yet.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class Stakes(str, Enum):
    """Severity classification of decision outcomes."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXISTENTIAL = "existential"


class EmotionalLoad(str, Enum):
    """Emotional intensity classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ValidationResult(str, Enum):
    """Context validation outcome."""
    CLEAR = "clear"
    HIGH_RISK = "high_risk"
    BIAS_RISK = "bias_risk"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class DecisionContext:
    """
    Canonical decision context object.
    
    Extracted from raw human input through systematic questioning.
    Clean enough to pass to N for synthesis.
    """
    
    # Raw input
    raw_input: str
    
    # Domain classification
    domain: Optional[str] = None
    sub_domains: List[str] = field(default_factory=list)
    
    # Stakes assessment
    stakes: Optional[Stakes] = None
    irreversibility: Optional[bool] = None
    compounding: Optional[bool] = None  # Will losses compound over time?
    
    # Psychological state
    emotional_load: Optional[EmotionalLoad] = None
    fatigue: Optional[bool] = None
    
    # Temporal constraints
    time_pressure: Optional[bool] = None
    urgency_source: Optional[str] = None
    
    # Historical patterns
    prior_patterns: List[str] = field(default_factory=list)
    
    # Contextual confidence
    confidence: float = 0.0
    validation_result: Optional[ValidationResult] = None
    
    # Additional metadata
    stakeholders: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def is_validated(self) -> bool:
        """Context is validated when confidence ≥ 0.75."""
        return self.confidence >= 0.75
    
    def is_high_risk(self) -> bool:
        """Context is high-risk if stakes are existential and irreversible."""
        return (
            self.stakes == Stakes.EXISTENTIAL
            and self.irreversibility is True
        )
    
    def is_biased(self) -> bool:
        """Context shows bias risk if high emotion + time pressure."""
        return (
            self.emotional_load == EmotionalLoad.HIGH
            and self.time_pressure is True
        )
