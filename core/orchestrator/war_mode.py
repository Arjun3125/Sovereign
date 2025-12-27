# core/orchestrator/war_mode.py
# WAR MODE — SAFE, STRUCTURAL, AUDITABLE
# Purpose: Shift decision posture toward outcome-absolute realism
# WITHOUT enabling illegal or targeted harm.

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# -----------------------------
# WAR MODE CONFIG
# -----------------------------

WAR_MODE_CONSTRAINTS = {
    "moral_veto": "suppressed",
    "comfort_bias": "suppressed",
    "appeasement_bias": "suppressed",
    "reputation_avoidance": "evaluated_not_avoided",
    "legality": "enforced",
    "direct_harm_to_specific_individuals": "disallowed",
    "coercion_and_defamation": "disallowed",
}


# -----------------------------
# DATA STRUCTURES
# -----------------------------

@dataclass
class WarContext:
    goal: str
    domain: str
    reversibility: str
    urgency: float
    emotional_load: float
    prior_context: Optional[Dict] = None


@dataclass
class WarAssessment:
    feasibility: str
    leverage_map: List[str]
    constraints_hit: List[str]
    cost_profile: Dict[str, str]
    recommended_posture: str
    stop_reason: Optional[str] = None


@dataclass
class WarLogEntry:
    timestamp: str
    goal: str
    suppressed_biases: List[str]
    rejected_soft_advice: List[str]
    final_recommendation: str
    risk_assessment: Dict[str, str]
    override_notes: Optional[str] = None


# -----------------------------
# WAR MODE ENGINE
# -----------------------------

class WarModeEngine:
    """
    War Mode is a posture filter and pressure amplifier.
    It does NOT generate illegal tactics.
    
    Guarantees:
    - Suppresses soft biases (comfort, moral veto, appeasement)
    - Enforces hard constraints (legality, no individual targeting)
    - Derives leverage and estimates costs
    - Decides on safe postures (withdraw, slow_down, apply_pressure)
    - Logs all decisions with full audit trail
    """

    def __init__(self):
        self.constraints = WAR_MODE_CONSTRAINTS
        self.logs: List[WarLogEntry] = []

    # ---------
    # CORE ENTRY
    # ---------

    def evaluate(self, context: WarContext) -> WarAssessment:
        """
        Evaluate War Mode feasibility and posture.
        
        Args:
            context: WarContext with goal, domain, reversibility, urgency, emotional_load
        
        Returns:
            WarAssessment with feasibility, leverage, costs, and recommended posture
        """
        constraints_hit = self._check_constraints(context)

        if constraints_hit:
            assessment = WarAssessment(
                feasibility="blocked",
                leverage_map=[],
                constraints_hit=constraints_hit,
                cost_profile={},
                recommended_posture="halt",
                stop_reason="Constraint violation: " + ", ".join(constraints_hit),
            )
            self.log(assessment, "Constraint violation detected")
            return assessment

        leverage = self._derive_leverage(context)
        cost = self._estimate_cost(context)

        posture = self._decide_posture(context, leverage, cost)

        assessment = WarAssessment(
            feasibility="viable",
            leverage_map=leverage,
            constraints_hit=[],
            cost_profile=cost,
            recommended_posture=posture,
        )
        self.log(assessment, None)
        return assessment

    # -----------------------------
    # INTERNAL LOGIC
    # -----------------------------

    def _check_constraints(self, context: WarContext) -> List[str]:
        """
        Check hard constraints (non-negotiable).
        
        Returns:
            List of violated constraints (empty if all pass)
        """
        violations = []

        # Explicit safety gate (non-negotiable)
        forbidden_signals = [
            "destroy reputation",
            "sabotage relationship",
            "coerce",
            "blackmail",
            "defame",
            "frame someone",
            "harm specific",
            "target individual",
        ]

        goal_lower = context.goal.lower()
        for signal in forbidden_signals:
            if signal in goal_lower:
                violations.append(f"forbidden_intent:{signal}")

        return violations

    def _derive_leverage(self, context: WarContext) -> List[str]:
        """
        Derive what leverage (safe, legal moves) is available.
        
        Returns:
            List of available leverage types
        """
        leverage = []

        if context.domain in ("career", "social", "status"):
            leverage.extend([
                "skill_compounding",
                "environment_selection",
                "signal_control",
                "optional_exit",
            ])

        if context.reversibility == "reversible":
            leverage.append("fast_iteration")

        if context.urgency > 0.7:
            leverage.append("tempo_advantage")

        if context.emotional_load < 0.5:
            leverage.append("decision_clarity")

        return leverage

    def _estimate_cost(self, context: WarContext) -> Dict[str, str]:
        """
        Estimate cost profile of War Mode posture.
        
        Returns:
            Dict with cost dimensions
        """
        cost = {
            "reputational": "medium",
            "emotional": "high" if context.emotional_load > 0.6 else "manageable",
            "reversibility": context.reversibility,
            "time_cost": "low" if context.urgency > 0.7 else "medium",
        }

        return cost

    def _decide_posture(
        self,
        context: WarContext,
        leverage: List[str],
        cost: Dict[str, str],
    ) -> str:
        """
        Decide on safe posture given leverage and costs.
        
        Options:
        - "halt": No safe path forward
        - "withdraw_and_reposition": Retreat to better ground
        - "slow_down_and_design_exits": Irreversible situation; plan carefully
        - "apply_pressure_structurally": Execute with leverage
        """
        if not leverage:
            return "withdraw_and_reposition"

        if cost["reversibility"] == "irreversible" and context.urgency > 0.7:
            return "slow_down_and_design_exits"

        if context.emotional_load > 0.7:
            return "withdraw_and_reposition"

        return "apply_pressure_structurally"

    # -----------------------------
    # LOGGING (MANDATORY)
    # -----------------------------

    def log(self, assessment: WarAssessment, notes: Optional[str] = None):
        """
        Log War Mode decision for audit trail.
        
        Args:
            assessment: WarAssessment result
            notes: Optional user override notes
        """
        entry = WarLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            goal=assessment.recommended_posture,
            suppressed_biases=[
                "comfort_bias",
                "appeasement_bias",
                "moral_veto",
            ],
            rejected_soft_advice=[
                "wait_for_alignment",
                "seek_harmony",
            ],
            final_recommendation=assessment.recommended_posture,
            risk_assessment=assessment.cost_profile,
            override_notes=notes,
        )
        self.logs.append(entry)

    def export_logs(self) -> List[Dict]:
        """
        Export all War Mode logs for inspection.
        
        Returns:
            List of log entry dicts
        """
        return [entry.__dict__ for entry in self.logs]

    def get_audit_trail(self) -> str:
        """
        Return human-readable audit trail.
        """
        lines = [
            "=" * 60,
            "WAR MODE AUDIT TRAIL",
            "=" * 60,
            "",
        ]

        for entry in self.logs:
            lines.append(f"[{entry.timestamp}] {entry.final_recommendation.upper()}")
            lines.append(f"  Suppressed biases: {', '.join(entry.suppressed_biases)}")
            lines.append(f"  Risks: {entry.risk_assessment}")
            if entry.override_notes:
                lines.append(f"  Notes: {entry.override_notes}")
            lines.append("")

        return "\n".join(lines)
