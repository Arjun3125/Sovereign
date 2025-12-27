"""
Outcome Tracker - Delayed Resolution Logging (LOCKED)

Outcomes are NOT logged immediately.

They're logged later via:
- Manual: resolve_event(event_id) — human reports outcome
- Automatic: After 7, 30, 90 days (if unresolved)

Captures:
- Result: success / partial / failure
- Damage: 0-1 scale
- Benefit: 0-1 scale
- Lessons: What was learned

Delayed outcomes enable:
- Distinguishing quick wins from trap decisions
- Long-term pattern detection
- Accurate minister calibration
"""

from typing import List, Optional
from datetime import datetime, timedelta
from core.memory.event_log import MemoryEvent


class OutcomeResolver:
    """
    Manages delayed resolution of decision outcomes.
    
    Outcomes logged days/weeks after initial decision,
    enabling long-term consequence assessment.
    """
    
    # Auto-resolve triggers (in days)
    AUTO_RESOLVE_DELAYS = [7, 30, 90]
    
    def __init__(self):
        """Initialize outcome resolver."""
        self.pending_resolutions: List[MemoryEvent] = []
    
    def resolve_event(
        self,
        event: MemoryEvent,
        result: str,  # "success" | "partial" | "failure"
        damage: float,  # 0-1 scale
        benefit: float,  # 0-1 scale
        lessons: List[str]
    ) -> bool:
        """
        Manually resolve outcome for an event.
        
        Args:
            event: Event to resolve
            result: How it turned out
            damage: Damage caused (0-1)
            benefit: Benefit gained (0-1)
            lessons: Lessons learned
            
        Returns:
            True if resolved, False if already resolved
        """
        if event.is_resolved():
            return False
        
        event.outcome_result = result
        event.outcome_damage = damage
        event.outcome_benefit = benefit
        event.outcome_lessons = lessons
        event.outcome_timestamp = datetime.now().timestamp()
        
        return True
    
    def get_pending_resolutions(
        self,
        events: List[MemoryEvent],
        days_old: int = 7
    ) -> List[MemoryEvent]:
        """
        Get events that should be auto-resolved.
        
        Args:
            events: All events
            days_old: Minimum age in days
            
        Returns:
            Events unresolved for at least days_old days
        """
        threshold = datetime.now().timestamp() - (days_old * 86400)
        
        pending = [
            e for e in events
            if not e.is_resolved() and e.timestamp < threshold
        ]
        
        return pending
    
    def auto_resolve_prompt(self, event: MemoryEvent, days: int) -> str:
        """
        Generate prompt to resolve old event.
        
        Args:
            event: Event to resolve
            days: How many days old
            
        Returns:
            Prompt string
        """
        return (
            f"Outcome check: {event.domain} decision from {days} days ago.\n"
            f"Verdict was: {event.verdict_position}\n"
            f"What happened? (success/partial/failure)"
        )
    
    def calculate_net_impact(
        self,
        events: List[MemoryEvent]
    ) -> dict:
        """
        Calculate net impact of resolved decisions.
        
        Args:
            events: All events
            
        Returns:
            Dict with impact metrics
        """
        resolved = [e for e in events if e.is_resolved()]
        
        if not resolved:
            return {
                "total_events_resolved": 0,
                "success_rate": 0.0,
                "average_benefit": 0.0,
                "average_damage": 0.0
            }
        
        successes = sum(1 for e in resolved if e.outcome_result == "success")
        partials = sum(1 for e in resolved if e.outcome_result == "partial")
        failures = sum(1 for e in resolved if e.outcome_result == "failure")
        
        avg_benefit = sum(e.outcome_benefit for e in resolved) / len(resolved)
        avg_damage = sum(e.outcome_damage for e in resolved) / len(resolved)
        
        return {
            "total_events_resolved": len(resolved),
            "successes": successes,
            "partials": partials,
            "failures": failures,
            "success_rate": successes / len(resolved),
            "average_benefit": avg_benefit,
            "average_damage": avg_damage,
            "net_impact": avg_benefit - avg_damage
        }
    
    def calculate_domain_impact(
        self,
        events: List[MemoryEvent],
        domain: str
    ) -> dict:
        """
        Calculate impact within specific domain.
        
        Args:
            events: All events
            domain: Domain to analyze
            
        Returns:
            Domain-specific impact metrics
        """
        domain_events = [e for e in events if e.domain == domain and e.is_resolved()]
        
        if not domain_events:
            return {
                "domain": domain,
                "total_resolved": 0,
                "success_rate": 0.0,
                "net_impact": 0.0
            }
        
        successes = sum(1 for e in domain_events if e.outcome_result == "success")
        avg_benefit = sum(e.outcome_benefit for e in domain_events) / len(domain_events)
        avg_damage = sum(e.outcome_damage for e in domain_events) / len(domain_events)
        
        return {
            "domain": domain,
            "total_resolved": len(domain_events),
            "success_rate": successes / len(domain_events),
            "average_benefit": avg_benefit,
            "average_damage": avg_damage,
            "net_impact": avg_benefit - avg_damage
        }
    
    def impact_summary(self, events: List[MemoryEvent]) -> str:
        """Generate human-readable impact summary."""
        impact = self.calculate_net_impact(events)
        
        if impact["total_events_resolved"] == 0:
            return "No resolved outcomes yet."
        
        lines = [
            f"OVERALL IMPACT ({impact['total_events_resolved']} resolved):\n",
            f"• Success rate: {impact['success_rate']:.0%}",
            f"• Successes: {impact['successes']}, Partials: {impact['partials']}, Failures: {impact['failures']}",
            f"• Average benefit: {impact['average_benefit']:.2f}",
            f"• Average damage: {impact['average_damage']:.2f}",
            f"• Net impact: {impact['net_impact']:+.2f}"
        ]
        
        return "\n".join(lines)
