"""
Event Log - Immutable Ledger of All Darbar Sessions (LOCKED)

Every decision cycle writes ONE immutable event.

Captures:
- Context summary
- Ministers called
- Verdict issued
- Posture taken
- Illusions detected
- Sovereign action (followed or overridden)

No edits. No deletions. Only append.
This is ground truth for pattern detection and confidence calibration.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class MemoryEvent:
    """
    Single immutable record of a Darbar session.
    
    Created when decision cycle completes.
    Updated only when outcome is resolved (later).
    Never edited retroactively.
    """
    
    # Identifiers
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    session_index: int = 0  # Sequential session number
    
    # Context
    domain: str = ""  # relationship, career, conflict, money, identity, other
    stakes: str = ""  # low, medium, high, existential
    emotional_load: str = ""  # low, medium, high
    
    # Execution
    ministers_called: List[str] = field(default_factory=list)
    verdict_position: str = ""  # What N recommended
    verdict_posture: str = ""  # abort, force, delay, conditional
    
    # Intelligence
    illusions_detected: List[str] = field(default_factory=list)
    contradictions_found: int = 0
    
    # Sovereign action
    sovereign_decision: str = ""  # What human actually did
    action_followed_counsel: bool = False  # True if matched verdict_posture
    
    # Override tracking
    override: bool = False
    override_reason: Optional[str] = None
    
    # Outcome (filled later)
    outcome_result: Optional[str] = None  # success, partial, failure
    outcome_damage: float = 0.0  # 0-1 scale
    outcome_benefit: float = 0.0  # 0-1 scale
    outcome_lessons: List[str] = field(default_factory=list)
    outcome_timestamp: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def is_resolved(self) -> bool:
        """Check if outcome has been logged."""
        return self.outcome_result is not None
    
    def was_overridden(self) -> bool:
        """Check if sovereign ignored counsel."""
        return self.override


class EventLog:
    """
    Immutable ledger of all Darbar sessions.
    
    Guarantees:
    - Append-only (no edits/deletions)
    - Timestamp ordered
    - Complete audit trail
    """
    
    def __init__(self):
        """Initialize event log."""
        self.events: List[MemoryEvent] = []
        self.session_counter = 0
    
    def create_event(
        self,
        domain: str,
        stakes: str,
        emotional_load: str,
        ministers_called: List[str],
        verdict_position: str,
        verdict_posture: str,
        illusions_detected: List[str],
        contradictions_found: int = 0
    ) -> MemoryEvent:
        """
        Create new event from decision cycle.
        
        Args:
            domain: Decision domain
            stakes: Stakes level
            emotional_load: Emotional load level
            ministers_called: Which ministers participated
            verdict_position: What N recommended
            verdict_posture: Posture (abort/force/delay/conditional)
            illusions_detected: Blind spots flagged
            contradictions_found: Count of structural contradictions
            
        Returns:
            New MemoryEvent (not yet saved)
        """
        self.session_counter += 1
        
        event = MemoryEvent(
            session_index=self.session_counter,
            domain=domain,
            stakes=stakes,
            emotional_load=emotional_load,
            ministers_called=ministers_called,
            verdict_position=verdict_position,
            verdict_posture=verdict_posture,
            illusions_detected=illusions_detected,
            contradictions_found=contradictions_found
        )
        
        return event
    
    def log_event(self, event: MemoryEvent) -> None:
        """
        Append event to immutable ledger.
        
        Args:
            event: MemoryEvent to append
        """
        self.events.append(event)
    
    def log_sovereign_action(
        self,
        event_id: str,
        sovereign_decision: str,
        action_followed_counsel: bool,
        override_reason: Optional[str] = None
    ) -> bool:
        """
        Update event with sovereign action taken.
        
        Fills in sovereign_decision, override flag, and override_reason.
        This is the ONLY update allowed to an event.
        
        Args:
            event_id: ID of event to update
            sovereign_decision: What sovereign did
            action_followed_counsel: Whether it matched verdict_posture
            override_reason: If overridden, why
            
        Returns:
            True if update successful, False if event not found
        """
        for event in self.events:
            if event.event_id == event_id:
                event.sovereign_decision = sovereign_decision
                event.action_followed_counsel = action_followed_counsel
                
                if not action_followed_counsel:
                    event.override = True
                    event.override_reason = override_reason
                
                return True
        
        return False
    
    def log_outcome(
        self,
        event_id: str,
        result: str,
        damage: float,
        benefit: float,
        lessons: List[str]
    ) -> bool:
        """
        Log outcome for an event (delayed, not immediate).
        
        Args:
            event_id: ID of event to update
            result: "success" | "partial" | "failure"
            damage: 0-1 scale of damage
            benefit: 0-1 scale of benefit
            lessons: List of lessons learned
            
        Returns:
            True if update successful
        """
        for event in self.events:
            if event.event_id == event_id:
                event.outcome_result = result
                event.outcome_damage = damage
                event.outcome_benefit = benefit
                event.outcome_lessons = lessons
                event.outcome_timestamp = datetime.now().timestamp()
                return True
        
        return False
    
    def get_event(self, event_id: str) -> Optional[MemoryEvent]:
        """Get specific event by ID."""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None
    
    def get_all_events(self) -> List[MemoryEvent]:
        """Get all events in chronological order."""
        return self.events.copy()
    
    def get_unresolved_events(self) -> List[MemoryEvent]:
        """Get events without outcome yet."""
        return [e for e in self.events if not e.is_resolved()]
    
    def get_events_by_domain(self, domain: str) -> List[MemoryEvent]:
        """Get all events in specific domain."""
        return [e for e in self.events if e.domain == domain]
    
    def get_overridden_events(self) -> List[MemoryEvent]:
        """Get all events where sovereign ignored counsel."""
        return [e for e in self.events if e.override]
