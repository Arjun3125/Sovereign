"""
Tribunal - Escalation Logic
Handles escalation and conflict resolution in the council.
"""

from typing import Dict, Any, List, Optional


class Tribunal:
    """
    Manages escalation and resolution of council disputes.
    
    When ministers conflict, tribunal provides sovereign judgment:
    - Weighs conflicting positions against stated goal
    - Identifies moral vs. strategic tradeoffs
    - Advises on acceptable risk thresholds
    """

    def __init__(self):
        """Initialize the tribunal."""
        pass

    def escalate(self, dispute: Dict[str, Any]) -> Optional[str]:
        """
        Escalate a dispute for sovereign judgment.
        
        Args:
            dispute: Dict with keys:
              - conflicts: List of conflict descriptions
              - positions: List of minister positions
              - goal: User's stated goal
              - state: Current state
        
        Returns:
            Judgment string (advice to sovereign)
        """
        conflicts = dispute.get("conflicts", [])
        positions = dispute.get("positions", [])
        goal = dispute.get("goal", "")
        state = dispute.get("state", {})

        if not conflicts:
            return None

        # Analyze conflict severity
        blocked_count = sum(1 for p in positions if p.get("status") == "STOP")
        clarification_count = sum(
            1 for p in positions if p.get("status") == "NEEDS_CLARIFICATION"
        )

        # Build judgment
        lines = [
            "TRIBUNAL JUDGMENT:",
        ]

        if blocked_count > 0:
            lines.append(
                f"⚠ {blocked_count} minister(s) flagged alignment issues with stated goal."
            )
            lines.append(
                "  → Recommend reviewing goal constraints before proceeding."
            )

        if clarification_count > 0:
            lines.append(
                f"❓ {clarification_count} minister(s) lack sufficient context."
            )
            lines.append(
                "  → Ask clarifying questions before committing to action."
            )

        # Risk assessment
        high_risk_positions = [
            p for p in positions if p.get("confidence", 1.0) < 0.65
        ]
        if high_risk_positions:
            lines.append(
                f"📊 {len(high_risk_positions)} position(s) have low confidence."
            )
            lines.append("  → Proceed with caution; monitor outcomes closely.")

        # Final judgment
        lines.append("")
        if blocked_count == 0 and clarification_count == 0:
            lines.append(
                "VERDICT: Council consensus achieved. Proceed with stated plan."
            )
        else:
            lines.append(
                "VERDICT: Address conflicts before executing plan. Consider staging approach."
            )

        return "\n".join(lines)
