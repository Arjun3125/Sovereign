"""
War Mode Logger - Audit trail for all War Mode decisions.

Documents:
- What biases were suppressed
- What advice was rejected (and why)
- Risk assessments
- Override notes
- Decision rationale

Enables later review: "You chose force posture here. Here's what it cost."
"""

from typing import Dict, Any, List
from datetime import datetime
import json


class WarModeLogger:
    """
    Logs all War Mode decisions with full audit trail.
    """
    
    def __init__(self):
        self.log_entries = []
        self.session_id = None
        self.session_start = None
    
    def start_session(self, goal: str, constraints: Dict[str, Any]) -> str:
        """
        Start a War Mode session.
        
        Args:
            goal: User's goal/objective
            constraints: Constraints being applied (suppressed biases, etc.)
        
        Returns:
            Session ID for tracking
        """
        self.session_id = self._generate_session_id()
        self.session_start = datetime.now().isoformat()
        
        self.log_entries.append({
            "timestamp": self.session_start,
            "event": "SESSION_START",
            "goal": goal,
            "suppressed_biases": [k for k, v in constraints.items() if v],
            "policy": constraints,
        })
        
        return self.session_id
    
    def log_advice_evaluation(
        self,
        minister: str,
        query: str,
        status: str,  # "APPROVED", "SUPPRESSED_SOFT", "REJECTED_HARD"
        advice: str,
        violations: List[str],
        suppressed_filters: List[str],
        confidence: float,
        citations: List[Dict[str, str]],
    ) -> None:
        """
        Log advice evaluation (retrieval + synthesis + filtering).
        
        Args:
            minister: Minister name
            query: Query that was used
            status: Result status
            advice: Advice text
            violations: Constraints violated
            suppressed_filters: Filters that were suppressed
            confidence: Confidence score
            citations: Source references
        """
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": "ADVICE_EVALUATION",
            "minister": minister,
            "query": query,
            "status": status,
            "advice": advice[:200] if advice else None,  # Truncate for log
            "violations": violations,
            "suppressed_filters": suppressed_filters,
            "confidence": confidence,
            "citation_count": len(citations),
        })
    
    def log_rejected_advice(
        self,
        minister: str,
        reason: str,
        soft_reason: bool = False,
    ) -> None:
        """
        Log advice that was rejected.
        
        Args:
            minister: Minister name
            reason: Why it was rejected
            soft_reason: True if soft constraint, False if hard constraint
        """
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": "ADVICE_REJECTED",
            "minister": minister,
            "reason": reason,
            "constraint_type": "soft" if soft_reason else "hard",
        })
    
    def log_risk_assessment(
        self,
        risk_level: str,  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
        description: str,
        mitigations: List[str],
    ) -> None:
        """
        Log risk assessment of final verdict.
        
        Args:
            risk_level: Risk severity
            description: What the risk is
            mitigations: How to mitigate
        """
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": "RISK_ASSESSMENT",
            "risk_level": risk_level,
            "description": description,
            "mitigations": mitigations,
        })
    
    def log_override_note(
        self,
        note: str,
        rationale: str,
    ) -> None:
        """
        Log when user provides override notes or context.
        
        Args:
            note: Override note text
            rationale: Why this override was needed
        """
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": "OVERRIDE_NOTE",
            "note": note,
            "rationale": rationale,
        })
    
    def end_session(self, final_verdict: str) -> Dict[str, Any]:
        """
        End War Mode session and return full log.
        
        Args:
            final_verdict: Final advice given to user
        
        Returns:
            Complete session log with audit trail
        """
        self.log_entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": "SESSION_END",
            "final_verdict_length": len(final_verdict),
        })
        
        # Compile session summary
        suppressed_count = sum(
            1 for e in self.log_entries
            if e.get("event") == "ADVICE_EVALUATION" and e.get("status") == "SUPPRESSED_SOFT"
        )
        rejected_count = sum(
            1 for e in self.log_entries
            if e.get("event") == "ADVICE_REJECTED"
        )
        
        session_log = {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat(),
            "summary": {
                "suppressed_soft_advice": suppressed_count,
                "rejected_hard_advice": rejected_count,
                "total_events": len(self.log_entries),
            },
            "entries": self.log_entries,
        }
        
        return session_log
    
    def get_audit_trail(self) -> str:
        """
        Return human-readable audit trail.
        """
        lines = [
            "=" * 60,
            "WAR MODE AUDIT TRAIL",
            f"Session: {self.session_id}",
            "=" * 60,
            "",
        ]
        
        for entry in self.log_entries:
            event = entry.get("event", "unknown")
            timestamp = entry.get("timestamp", "")
            
            if event == "SESSION_START":
                lines.append(f"[{timestamp}] SESSION START")
                lines.append(f"  Goal: {entry.get('goal')}")
                lines.append(
                    f"  Suppressed biases: {', '.join(entry.get('suppressed_biases', []))}"
                )
            
            elif event == "ADVICE_EVALUATION":
                lines.append(f"[{timestamp}] {entry.get('minister')} - {entry.get('status')}")
                if entry.get("suppressed_filters"):
                    lines.append(
                        f"  Suppressed: {', '.join(entry.get('suppressed_filters', []))}"
                    )
            
            elif event == "ADVICE_REJECTED":
                lines.append(f"[{timestamp}] REJECTED - {entry.get('minister')}")
                lines.append(f"  Reason: {entry.get('reason')}")
            
            elif event == "RISK_ASSESSMENT":
                lines.append(f"[{timestamp}] RISK: {entry.get('risk_level')}")
                lines.append(f"  {entry.get('description')}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"war_{uuid.uuid4().hex[:12]}"
