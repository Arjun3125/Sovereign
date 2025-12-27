"""
Confidence Adjuster - Minister Calibration (LOCKED)

Updates minister credibility based on outcome accuracy.

Logic:
- Minister verdict correct → confidence += 0.05
- Minister verdict partially correct → no change
- Minister verdict incorrect → confidence -= 0.05

Prevents:
- Blind faith in any single minister
- Permanent authority (everyone starts at 0.5)
- Ignoring domain expertise

Calibration is per-domain:
- Power minister highly accurate on conflict
- Psychology minister less accurate on timing
- Etc.

Result: N weights verdicts more accurately over time.
"""

from typing import Dict, List
from core.memory.event_log import MemoryEvent


class MinisterCalibration:
    """
    Tracks minister accuracy per domain.
    
    Starts: confidence = 0.5 (neutral)
    Updates: +0.05 per correct, -0.05 per incorrect
    Range: 0.0 (never trust) to 1.0 (always trust)
    """
    
    INITIAL_CONFIDENCE = 0.5
    CORRECT_ADJUSTMENT = 0.05
    INCORRECT_ADJUSTMENT = -0.05
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0
    
    def __init__(self):
        """Initialize minister calibrations."""
        # Structure: { minister_name: { domain: confidence } }
        self.calibrations: Dict[str, Dict[str, float]] = {}
    
    def get_confidence(self, minister: str, domain: str) -> float:
        """
        Get minister's confidence in specific domain.
        
        Args:
            minister: Minister name
            domain: Decision domain
            
        Returns:
            Confidence score (0.0-1.0)
        """
        if minister not in self.calibrations:
            return self.INITIAL_CONFIDENCE
        
        return self.calibrations[minister].get(domain, self.INITIAL_CONFIDENCE)
    
    def adjust_confidence(
        self,
        minister: str,
        domain: str,
        outcome_result: str  # "success" | "partial" | "failure"
    ) -> float:
        """
        Adjust minister confidence based on outcome.
        
        Args:
            minister: Minister name
            domain: Decision domain
            outcome_result: How the decision turned out
            
        Returns:
            New confidence score
        """
        if minister not in self.calibrations:
            self.calibrations[minister] = {}
        
        current = self.calibrations[minister].get(domain, self.INITIAL_CONFIDENCE)
        
        # Determine adjustment
        if outcome_result == "success":
            adjustment = self.CORRECT_ADJUSTMENT
        elif outcome_result == "partial":
            adjustment = 0.0  # No change for partial
        else:  # failure
            adjustment = self.INCORRECT_ADJUSTMENT
        
        # Apply adjustment with bounds
        new_confidence = max(
            self.MIN_CONFIDENCE,
            min(self.MAX_CONFIDENCE, current + adjustment)
        )
        
        self.calibrations[minister][domain] = new_confidence
        
        return new_confidence
    
    def adjust_for_events(self, events: List[MemoryEvent]) -> None:
        """
        Batch-adjust calibrations based on resolved events.
        
        Args:
            events: All events (some may have outcomes)
        """
        for event in events:
            if not event.is_resolved():
                continue
            
            # Adjust all ministers who were called in this event
            for minister in event.ministers_called:
                self.adjust_confidence(
                    minister,
                    event.domain,
                    event.outcome_result
                )
    
    def get_minister_domains(self, minister: str) -> Dict[str, float]:
        """
        Get all calibrations for a minister (all domains).
        
        Args:
            minister: Minister name
            
        Returns:
            Dict of domain -> confidence
        """
        return self.calibrations.get(minister, {}).copy()
    
    def get_domain_experts(self, domain: str) -> List[tuple]:
        """
        Get ministers ranked by confidence in domain.
        
        Args:
            domain: Decision domain
            
        Returns:
            List of (minister, confidence) sorted by confidence desc
        """
        experts = []
        
        for minister, domains in self.calibrations.items():
            confidence = domains.get(domain, self.INITIAL_CONFIDENCE)
            experts.append((minister, confidence))
        
        return sorted(experts, key=lambda x: x[1], reverse=True)
    
    def calibration_summary(self) -> str:
        """Generate summary of all calibrations."""
        if not self.calibrations:
            return "No calibrations yet (all ministers at default 0.5)."
        
        lines = ["MINISTER CALIBRATIONS:\n"]
        
        for minister in sorted(self.calibrations.keys()):
            domains = self.calibrations[minister]
            
            if domains:
                avg_conf = sum(domains.values()) / len(domains)
                lines.append(
                    f"• {minister}: avg {avg_conf:.2f} "
                    f"({len(domains)} domains tracked)"
                )
        
        return "\n".join(lines)
    
    def domain_calibration_summary(self, domain: str) -> str:
        """Generate summary of calibrations in specific domain."""
        experts = self.get_domain_experts(domain)
        
        lines = [f"CALIBRATIONS IN {domain}:\n"]
        
        for minister, confidence in experts[:5]:  # Top 5
            lines.append(f"• {minister}: {confidence:.2f}")
        
        return "\n".join(lines)
