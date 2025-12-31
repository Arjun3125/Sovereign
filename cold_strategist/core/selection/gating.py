"""
Gating Rules - Noise Control for Minister Selection (LOCKED)

Prevents too many voices from muddying analysis.
Default: max 3 ministers
Exception: chaos conditions allow up to 5

Chaos conditions:
- Domain is "conflict"
- AND irreversibility is true
- AND emotional load is high

Otherwise: trim to 3 for focused debate.
"""

from typing import List, Tuple
from context.context_schema import DecisionContext, EmotionalLoad


class SelectionGating:
    """
    Applies noise control rules to minister selection.
    
    Too many ministers = unfocused debate
    Too few = missing perspectives
    
    Sweet spot: 3 ministers
    Exception: 5 if chaos conditions met
    """
    
    DEFAULT_MAX = 3
    CHAOS_MAX = 5
    
    def apply(
        self,
        ctx: DecisionContext,
        selected: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """
        Apply gating rules to selected ministers.
        
        Args:
            ctx: Decision context
            selected: List of (minister, score) tuples
            
        Returns:
            Gated list (may be shorter)
        """
        # Always allow 2 or fewer
        if len(selected) <= 2:
            return selected
        
        # Check chaos conditions
        if self._is_chaos_situation(ctx):
            max_allowed = self.CHAOS_MAX
        else:
            max_allowed = self.DEFAULT_MAX
        
        return selected[:max_allowed]
    
    def _is_chaos_situation(self, ctx: DecisionContext) -> bool:
        """
        Determine if this is a chaos situation (richer debate needed).
        
        Chaos = conflict + irreversibility + high emotion
        
        Args:
            ctx: Decision context
            
        Returns:
            True if chaos conditions met
        """
        return (
            ctx.domain == "conflict"
            and ctx.irreversibility is True
            and ctx.emotional_load == EmotionalLoad.HIGH
        )
    
    def get_max_ministers(self, ctx: DecisionContext) -> int:
        """
        Get maximum allowed ministers for this context.
        
        Args:
            ctx: Decision context
            
        Returns:
            Max number of ministers (3 or 5)
        """
        return self.CHAOS_MAX if self._is_chaos_situation(ctx) else self.DEFAULT_MAX
    
    def gating_explanation(self, ctx: DecisionContext) -> str:
        """
        Generate explanation of gating decision.
        
        Args:
            ctx: Decision context
            
        Returns:
            String explanation
        """
        if self._is_chaos_situation(ctx):
            return (
                "CHAOS SITUATION: conflict + irreversibility + high emotion. "
                f"Allowing up to {self.CHAOS_MAX} ministers for richer debate."
            )
        else:
            return (
                f"Normal situation. Limiting to {self.DEFAULT_MAX} ministers "
                "for focused debate."
            )
