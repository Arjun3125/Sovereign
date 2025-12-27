"""
Memory Store - SQLite Persistence Layer (LOCKED v1)

Production-grade storage using SQLite.

Guarantees:
- ACID transactions
- Immutable event log (INSERT-only)
- Queryable patterns and outcomes
- Zero doctrine mutation
- Easy backup and export

Database location: data/memory/cold_strategist.db
Schema: data/memory/schema.sql (versioned)
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid
from core.memory.database import Database
from core.memory.event_log import MemoryEvent, EventLog
from core.memory.pattern_engine import Pattern, PatternEngine
from core.memory.override_tracker import OverrideRecord, OverrideTracker
from core.memory.confidence_adjuster import MinisterCalibration


class MemoryStore:
    """
    SQLite-backed memory persistence.
    
    All memory operations go through this layer.
    Ensures ACID guarantees and queryability.
    """
    
    def __init__(self):
        """Initialize memory store with SQLite."""
        self.db = Database()
    
    # ========================================================================
    # EVENT OPERATIONS
    # ========================================================================
    
    def save_event(self, event: MemoryEvent) -> None:
        """
        Save event to ledger (INSERT-only).
        
        Args:
            event: MemoryEvent to save
        """
        self.db.insert_event(
            event_id=event.event_id,
            timestamp=int(event.timestamp),
            session_index=event.session_index,
            domain=event.domain,
            stakes=event.stakes,
            emotional_load=0.0 if not event.emotional_load else (
                0.33 if event.emotional_load == "low" else
                0.66 if event.emotional_load == "medium" else
                1.0
            ),
            urgency=0.0,  # TODO: extract from context
            ministers_called=event.ministers_called,
            verdict=event.verdict_position,
            posture=event.verdict_posture,
            illusions_detected=event.illusions_detected,
            contradictions_found=event.contradictions_found,
            sovereign_action=event.sovereign_decision,
            action_followed_counsel=event.action_followed_counsel,
            override_reason=event.override_reason
        )
    
    def load_events(self) -> List[MemoryEvent]:
        """
        Load all events from ledger.
        
        Returns:
            List of MemoryEvent objects
        """
        events = []
        db_events = self.db.get_all_events()
        
        for row in db_events:
            event = self._row_to_event(row)
            events.append(event)
        
        return events
    
    def get_event(self, event_id: str) -> Optional[MemoryEvent]:
        """Get single event by ID."""
        row = self.db.get_event(event_id)
        return self._row_to_event(row) if row else None
    
    # ========================================================================
    # OUTCOME OPERATIONS
    # ========================================================================
    
    def save_outcome(
        self,
        event_id: str,
        result: str,
        damage: float,
        benefit: float,
        lessons: List[str]
    ) -> None:
        """
        Save outcome for event (delayed resolution).
        
        Args:
            event_id: Event ID being resolved
            result: "success" | "partial" | "failure"
            damage: 0-1 scale
            benefit: 0-1 scale
            lessons: Lessons learned
        """
        self.db.insert_outcome(
            event_id=event_id,
            resolved_at=int(datetime.now().timestamp()),
            result=result,
            damage=damage,
            benefit=benefit,
            lessons=lessons
        )
    
    # ========================================================================
    # PATTERN OPERATIONS
    # ========================================================================
    
    def save_patterns(self, patterns: List[Pattern]) -> None:
        """
        Save detected patterns (rebuild entire set).
        
        Args:
            patterns: List of patterns to save
        """
        for pattern in patterns:
            self.db.insert_pattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type=pattern.pattern_type,
                description=pattern.pattern_name,
                domain=pattern.domain,
                illusion_type=pattern.illusion_type,
                frequency=pattern.frequency,
                last_seen=None,
                last_outcome=pattern.last_outcome
            )
    
    def load_patterns(self) -> List[Pattern]:
        """
        Load detected patterns.
        
        Returns:
            List of Pattern objects
        """
        patterns = []
        db_patterns = self.db.get_patterns()
        
        for row in db_patterns:
            pattern = Pattern(
                pattern_name=row["description"],
                pattern_type=row["pattern_type"],
                frequency=row["frequency"],
                domain=row["domain"],
                illusion_type=row["illusion_type"],
                last_outcome=row["last_outcome"]
            )
            patterns.append(pattern)
        
        return patterns
    
    # ========================================================================
    # CALIBRATION OPERATIONS
    # ========================================================================
    
    def save_calibrations(self, calibrations: MinisterCalibration) -> None:
        """
        Save minister calibrations.
        
        Args:
            calibrations: MinisterCalibration object
        """
        for minister, domains in calibrations.calibrations.items():
            for domain, confidence in domains.items():
                self.db.set_calibration(minister, domain, confidence)
    
    def load_calibrations(self) -> MinisterCalibration:
        """
        Load all minister calibrations.
        
        Returns:
            MinisterCalibration object
        """
        calibrations = MinisterCalibration()
        db_calibrations = self.db.get_all_calibrations()
        calibrations.calibrations = db_calibrations
        return calibrations
    
    # ========================================================================
    # OVERRIDE OPERATIONS
    # ========================================================================
    
    def save_override(self, override: OverrideRecord) -> None:
        """
        Save override record.
        
        Args:
            override: OverrideRecord to save
        """
        self.db.insert_override(
            override_id=str(uuid.uuid4()),
            event_id=override.event_id,
            domain=override.domain,
            counsel_posture=override.counsel_posture,
            actual_action=override.actual_action,
            override_reason=override.override_reason
        )
    
    def load_overrides(self) -> List[OverrideRecord]:
        """
        Load all override records.
        
        Returns:
            List of OverrideRecord objects
        """
        overrides = []
        # TODO: Load from database
        return overrides
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def memory_summary(self) -> str:
        """Generate summary of stored memory."""
        stats = self.db.stats()
        
        return f"""
MEMORY STORE SUMMARY:

• Events: {stats['events']} total
• Outcomes resolved: {stats['outcomes']}
• Patterns detected: {stats['patterns']}
• Overrides: {stats['overrides']}

Store: data/memory/cold_strategist.db
Schema: v1.0
""".strip()
    
    # ========================================================================
    # INTERNAL
    # ========================================================================
    
    def _row_to_event(self, row: dict) -> MemoryEvent:
        """Convert database row to MemoryEvent."""
        import json
        
        event = MemoryEvent(
            event_id=row["id"],
            timestamp=float(row["timestamp"]),
            session_index=row["session_index"],
            domain=row["domain"],
            stakes=row["stakes"],
            emotional_load="low" if row["emotional_load"] < 0.33 else
                          "medium" if row["emotional_load"] < 0.66 else
                          "high",
            ministers_called=json.loads(row["ministers_called"]),
            verdict_position=row["verdict"],
            verdict_posture=row["posture"],
            illusions_detected=json.loads(row["illusions_detected"] or "[]"),
            contradictions_found=row["contradictions_found"],
            sovereign_decision=row["sovereign_action"],
            action_followed_counsel=bool(row["action_followed_counsel"]),
            override=not bool(row["action_followed_counsel"]),
            override_reason=row["override_reason"]
        )
        
        # Load outcome if exists
        outcome = self.db.get_outcome(row["id"])
        if outcome:
            import json
            event.outcome_result = outcome["result"]
            event.outcome_damage = outcome["damage"]
            event.outcome_benefit = outcome["benefit"]
            event.outcome_lessons = json.loads(outcome["lessons"] or "[]")
            event.outcome_timestamp = outcome["resolved_at"]
        
        return event
