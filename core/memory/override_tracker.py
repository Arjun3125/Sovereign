"""
Override Tracker - Counsel Ignored Log (LOCKED)

Tracks when sovereign ignores minister counsel.

Each override is logged with:
- What was recommended
- What was done instead
- Outcome (later)

Overrides increase future bluntness:
- Repeated ignore of same domain → harsher language
- Repeated override despite warnings → shorter counsel
- Override before outcome known → flagged for pattern analysis

Enables progression:
Session 1: "Consider that..."
Session 3: "You're repeating..."
Session 5: "Stop doing this."
"""

from typing import List, Dict, Optional
from core.memory.event_log import MemoryEvent


class OverrideRecord:
    """Single recorded override."""
    
    def __init__(
        self,
        event_id: str,
        domain: str,
        counsel_posture: str,
        actual_action: str,
        override_reason: Optional[str] = None
    ):
        self.event_id = event_id
        self.domain = domain
        self.counsel_posture = counsel_posture
        self.actual_action = actual_action
        self.override_reason = override_reason
        self.outcome_result: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "domain": self.domain,
            "counsel_posture": self.counsel_posture,
            "actual_action": self.actual_action,
            "override_reason": self.override_reason,
            "outcome": self.outcome_result
        }


class OverrideTracker:
    """
    Tracks all instances of sovereign overriding counsel.
    
    Used to:
    1. Detect override patterns
    2. Increase bluntness on repeat ignores
    3. Flag counselor credibility
    """
    
    def __init__(self):
        """Initialize override tracker."""
        self.overrides: List[OverrideRecord] = []
    
    def log_override(
        self,
        event: MemoryEvent,
        counsel_posture: str,
        actual_action: str,
        override_reason: Optional[str] = None
    ) -> OverrideRecord:
        """
        Record an override.
        
        Args:
            event: The event that was overridden
            counsel_posture: What N recommended
            actual_action: What sovereign did instead
            override_reason: Why sovereign overrode (optional)
            
        Returns:
            The OverrideRecord created
        """
        override = OverrideRecord(
            event_id=event.event_id,
            domain=event.domain,
            counsel_posture=counsel_posture,
            actual_action=actual_action,
            override_reason=override_reason
        )
        
        self.overrides.append(override)
        return override
    
    def log_override_outcome(self, event_id: str, outcome: str) -> bool:
        """
        Update override with its outcome.
        
        Args:
            event_id: ID of overridden event
            outcome: "success" | "partial" | "failure"
            
        Returns:
            True if updated, False if not found
        """
        for override in self.overrides:
            if override.event_id == event_id:
                override.outcome_result = outcome
                return True
        return False
    
    def get_overrides_by_domain(self, domain: str) -> List[OverrideRecord]:
        """Get all overrides in specific domain."""
        return [o for o in self.overrides if o.domain == domain]
    
    def get_failed_overrides(self) -> List[OverrideRecord]:
        """Get overrides that resulted in failure."""
        return [o for o in self.overrides if o.outcome_result == "failure"]
    
    def get_successful_overrides(self) -> List[OverrideRecord]:
        """Get overrides that resulted in success."""
        return [o for o in self.overrides if o.outcome_result == "success"]
    
    def override_frequency(self, domain: str) -> int:
        """Count overrides in domain."""
        return len(self.get_overrides_by_domain(domain))
    
    def override_success_rate(self, domain: str) -> float:
        """Calculate success rate of overrides in domain."""
        domain_overrides = self.get_overrides_by_domain(domain)
        resolved = [o for o in domain_overrides if o.outcome_result]
        
        if not resolved:
            return 0.0
        
        successes = sum(1 for o in resolved if o.outcome_result == "success")
        return successes / len(resolved)
    
    def get_bluntness_level(self, domain: str) -> str:
        """
        Determine tone bluntness based on override frequency.
        
        Args:
            domain: Decision domain
            
        Returns:
            "gentle" | "direct" | "harsh" | "final_warning"
        """
        frequency = self.override_frequency(domain)
        success_rate = self.override_success_rate(domain)
        
        # Many overrides with poor outcomes = harsh tone
        if frequency >= 5 and success_rate < 0.3:
            return "final_warning"
        
        if frequency >= 4:
            return "harsh"
        
        if frequency >= 2:
            return "direct"
        
        return "gentle"
    
    def override_summary(self) -> str:
        """Generate summary of override patterns."""
        if not self.overrides:
            return "No overrides recorded."
        
        lines = [f"OVERRIDE SUMMARY ({len(self.overrides)} total):\n"]
        
        # Group by domain
        by_domain = {}
        for override in self.overrides:
            if override.domain not in by_domain:
                by_domain[override.domain] = []
            by_domain[override.domain].append(override)
        
        for domain, domain_overrides in by_domain.items():
            success_rate = self.override_success_rate(domain)
            bluntness = self.get_bluntness_level(domain)
            
            lines.append(
                f"• {domain}: {len(domain_overrides)} overrides, "
                f"{success_rate:.0%} success rate, "
                f"tone: {bluntness}"
            )
        
        return "\n".join(lines)
