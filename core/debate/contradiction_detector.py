"""
Contradiction Detector - Structural Conflict Identification (LOCKED)

Scans minister verdicts for internal strategic contradictions.

Detects:
- Strategy vs Survival
- Power vs Legitimacy
- Speed vs Reversibility
- Desire vs Trajectory

Each contradiction flagged and tagged for N synthesis.
"""

from typing import List, Tuple
from core.debate.debate_schema import MinisterVerdict, VerdictType
import re


class ContradictionType:
    """Canonical contradiction categories."""
    
    STRATEGY_VS_SURVIVAL = "strategy_vs_survival"
    POWER_VS_LEGITIMACY = "power_vs_legitimacy"
    SPEED_VS_REVERSIBILITY = "speed_vs_reversibility"
    DESIRE_VS_TRAJECTORY = "desire_vs_trajectory"
    FEASIBILITY_CONFIDENCE_MISMATCH = "feasibility_confidence_mismatch"


class Contradiction:
    """A detected structural conflict in minister positions."""
    
    def __init__(
        self,
        contradiction_type: str,
        minister_a: str,
        minister_b: str,
        description: str,
        severity: str = "medium"
    ):
        self.type = contradiction_type
        self.minister_a = minister_a
        self.minister_b = minister_b
        self.description = description
        self.severity = severity  # low / medium / high
    
    def __repr__(self):
        return (
            f"Contradiction({self.type}, {self.minister_a} vs {self.minister_b}, "
            f"severity={self.severity})"
        )


class ContradictionDetector:
    """
    Finds structural conflicts in minister debate verdicts.
    
    Not just disagreement—but actual incompatible positions.
    Surfaces them for N to synthesize.
    """
    
    def __init__(self):
        """Initialize detector."""
        self.verdicts: List[MinisterVerdict] = []
    
    def detect_all(self, verdicts: List[MinisterVerdict]) -> List[Contradiction]:
        """
        Scan all verdicts and return detected contradictions.
        
        Args:
            verdicts: List of minister verdicts
            
        Returns:
            List of Contradiction objects
        """
        self.verdicts = verdicts
        contradictions = []
        
        # Pairwise comparison
        for i, v_a in enumerate(verdicts):
            for v_b in verdicts[i+1:]:
                detected = self._compare_verdicts(v_a, v_b)
                contradictions.extend(detected)
        
        # Internal analysis (single verdict can contradict itself)
        for verdict in verdicts:
            internal = self._check_internal_consistency(verdict)
            contradictions.extend(internal)
        
        return contradictions
    
    def _compare_verdicts(
        self,
        v_a: MinisterVerdict,
        v_b: MinisterVerdict
    ) -> List[Contradiction]:
        """
        Compare two verdicts for contradictions.
        
        Args:
            v_a: First verdict
            v_b: Second verdict
            
        Returns:
            List of contradictions found
        """
        contradictions = []
        
        # Strategy vs Survival
        if self._is_strategy_vs_survival(v_a, v_b):
            contradictions.append(
                Contradiction(
                    ContradictionType.STRATEGY_VS_SURVIVAL,
                    v_a.minister_name,
                    v_b.minister_name,
                    f"{v_a.minister_name} prioritizes strategy (confident position); "
                    f"{v_b.minister_name} warns survival risk. "
                    f"Incompatible risk tolerance.",
                    severity="high"
                )
            )
        
        # Power vs Legitimacy
        if self._is_power_vs_legitimacy(v_a, v_b):
            contradictions.append(
                Contradiction(
                    ContradictionType.POWER_VS_LEGITIMACY,
                    v_a.minister_name,
                    v_b.minister_name,
                    f"{v_a.minister_name} emphasizes power/advantage; "
                    f"{v_b.minister_name} emphasizes legitimacy/acceptance. "
                    f"Action may not survive scrutiny.",
                    severity="medium"
                )
            )
        
        # Speed vs Reversibility
        if self._is_speed_vs_reversibility(v_a, v_b):
            contradictions.append(
                Contradiction(
                    ContradictionType.SPEED_VS_REVERSIBILITY,
                    v_a.minister_name,
                    v_b.minister_name,
                    f"{v_a.minister_name} pushes speed; "
                    f"{v_b.minister_name} warns irreversibility. "
                    f"Cannot have both fast AND reversible.",
                    severity="high"
                )
            )
        
        # Desire vs Trajectory
        if self._is_desire_vs_trajectory(v_a, v_b):
            contradictions.append(
                Contradiction(
                    ContradictionType.DESIRE_VS_TRAJECTORY,
                    v_a.minister_name,
                    v_b.minister_name,
                    f"{v_a.minister_name} focuses on immediate outcome; "
                    f"{v_b.minister_name} warns long-term trajectory damage. "
                    f"Short-term win may lock into worse future.",
                    severity="medium"
                )
            )
        
        return contradictions
    
    def _check_internal_consistency(self, verdict: MinisterVerdict) -> List[Contradiction]:
        """
        Check if a single verdict contradicts itself.
        
        Args:
            verdict: Minister verdict
            
        Returns:
            List of internal contradictions
        """
        contradictions = []
        
        # Low confidence but high viability claim
        if verdict.confidence < 0.4 and verdict.verdict_type == VerdictType.VIABLE:
            contradictions.append(
                Contradiction(
                    ContradictionType.FEASIBILITY_CONFIDENCE_MISMATCH,
                    verdict.minister_name,
                    verdict.minister_name,
                    f"{verdict.minister_name} claims position is viable "
                    f"but only {verdict.confidence:.0%} confident. "
                    f"Position is conditionally viable at best.",
                    severity="medium"
                )
            )
        
        return contradictions
    
    def _is_strategy_vs_survival(self, v_a: MinisterVerdict, v_b: MinisterVerdict) -> bool:
        """Detect strategy vs survival contradiction."""
        strategy_keywords = ["advantage", "leverage", "benefit", "gain", "win"]
        survival_keywords = ["ruin", "collapse", "extinction", "loss", "catastrophe"]
        
        a_text = (v_a.position + " " + v_a.warning).lower()
        b_text = (v_b.position + " " + b_text).lower()
        
        a_is_strategy = any(k in a_text for k in strategy_keywords)
        a_is_survival = any(k in a_text for k in survival_keywords)
        
        b_is_strategy = any(k in b_text for k in strategy_keywords)
        b_is_survival = any(k in b_text for k in survival_keywords)
        
        return (a_is_strategy and b_is_survival) or (a_is_survival and b_is_strategy)
    
    def _is_power_vs_legitimacy(self, v_a: MinisterVerdict, v_b: MinisterVerdict) -> bool:
        """Detect power vs legitimacy contradiction."""
        power_keywords = ["force", "leverage", "dominate", "enforce", "coerce"]
        legitimacy_keywords = ["consent", "authority", "trust", "norms", "acceptance"]
        
        a_text = (v_a.position + " " + v_a.warning).lower()
        b_text = (v_b.position + " " + v_b.warning).lower()
        
        a_power = any(k in a_text for k in power_keywords)
        a_legit = any(k in a_text for k in legitimacy_keywords)
        
        b_power = any(k in b_text for k in power_keywords)
        b_legit = any(k in b_text for k in legitimacy_keywords)
        
        return (a_power and b_legit) or (a_legit and b_power)
    
    def _is_speed_vs_reversibility(self, v_a: MinisterVerdict, v_b: MinisterVerdict) -> bool:
        """Detect speed vs reversibility contradiction."""
        speed_keywords = ["fast", "immediate", "quick", "urgent", "now"]
        revert_keywords = ["reverse", "undo", "reversible", "exit", "retreat"]
        
        a_text = (v_a.position + " " + v_a.warning).lower()
        b_text = (v_b.position + " " + v_b.warning).lower()
        
        a_speed = any(k in a_text for k in speed_keywords)
        a_revert = any(k in a_text for k in revert_keywords)
        
        b_speed = any(k in b_text for k in speed_keywords)
        b_revert = any(k in b_text for k in revert_keywords)
        
        return (a_speed and b_revert) or (a_revert and b_speed)
    
    def _is_desire_vs_trajectory(self, v_a: MinisterVerdict, v_b: MinisterVerdict) -> bool:
        """Detect desire (immediate) vs trajectory (long-term) contradiction."""
        immediate_keywords = ["now", "today", "immediate", "short-term"]
        trajectory_keywords = ["future", "long-term", "path", "trajectory", "compound"]
        
        a_text = (v_a.position + " " + v_a.warning).lower()
        b_text = (v_b.position + " " + v_b.warning).lower()
        
        a_immediate = any(k in a_text for k in immediate_keywords)
        a_trajectory = any(k in a_text for k in trajectory_keywords)
        
        b_immediate = any(k in b_text for k in immediate_keywords)
        b_trajectory = any(k in b_text for k in trajectory_keywords)
        
        return (a_immediate and b_trajectory) or (a_trajectory and b_immediate)
