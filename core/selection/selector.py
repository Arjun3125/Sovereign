"""
Minister Selector - Context-Driven Minister Selection (LOCKED)

Selects which ministers should participate based on context relevance.
Deterministic. Score-based. Hard cutoff at 3.
Gating rules prevent noise.

Flow:
1. Score all ministers
2. Select those scoring ≥ 3
3. Apply gating rules (max 3 unless chaos conditions met)
4. Return ranked list to orchestrator
"""

from typing import List, Tuple
from context.context_schema import DecisionContext, Stakes, EmotionalLoad
from core.selection.minister_registry import MINISTERS
from core.selection.contribution_matrix import ContributionMatrix


class MinisterSelector:
    """
    Selects which ministers should participate in this decision.
    
    Selection is purely fact-based:
    - Score all ministers
    - Keep those scoring ≥ 3
    - Apply gating (noise control)
    - Return ranked list
    """
    
    def __init__(self, matrix: ContributionMatrix = None):
        """
        Initialize selector.
        
        Args:
            matrix: ContributionMatrix instance (or create default)
        """
        self.matrix = matrix or ContributionMatrix()
    
    def select(self, ctx: DecisionContext) -> List[Tuple[str, int]]:
        """
        Select ministers for this context.
        
        Args:
            ctx: Decision context
            
        Returns:
            List of (minister_name, score) tuples, ranked by score descending
        """
        # Get all ministers scoring >= minimum
        qualified = self.matrix.ministers_above_threshold(ctx)
        
        # Apply gating rules
        gated = self._apply_gating(ctx, qualified)
        
        return gated
    
    def _apply_gating(
        self,
        ctx: DecisionContext,
        qualified: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """
        Apply noise control gating rules.
        
        Default: max 3 ministers
        Exception: if chaos conditions met (conflict + irreversibility + emotion),
        allow up to 5 for richer debate
        
        Args:
            ctx: Decision context
            qualified: List of (minister, score) tuples
            
        Returns:
            Gated list of ministers
        """
        if len(qualified) <= 2:
            return qualified
        
        # Chaos conditions: allow richer debate
        has_conflict_domain = ctx.domain == "conflict"
        has_irreversibility = ctx.irreversibility is True
        has_emotion = ctx.emotional_load == EmotionalLoad.HIGH
        
        if has_conflict_domain and has_irreversibility and has_emotion:
            # High-stakes conflict with emotion: allow more voices
            return qualified[:5]
        
        # Normal case: limit to 3 for focused debate
        return qualified[:3]
    
    def selection_summary(
        self,
        ctx: DecisionContext,
        selected: List[Tuple[str, int]]
    ) -> dict:
        """
        Generate human-readable summary of selection.
        
        Args:
            ctx: Decision context
            selected: Selected ministers (from select())
            
        Returns:
            Summary dict with context summary and minister explanations
        """
        return {
            "context": {
                "domain": ctx.domain,
                "stakes": ctx.stakes.value if ctx.stakes else None,
                "irreversibility": ctx.irreversibility,
                "emotional_load": ctx.emotional_load.value if ctx.emotional_load else None,
                "time_pressure": ctx.time_pressure,
                "confidence": ctx.confidence
            },
            "selected_ministers": [
                {
                    "minister": minister,
                    "score": score,
                    "reason": self.matrix.score_explanation(ctx, minister)
                }
                for minister, score in selected
            ],
            "total_selected": len(selected)
        }
