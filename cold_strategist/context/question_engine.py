"""
Question Engine - Systematic Context Extraction (LOCKED)

Generates only necessary questions to reach confidence threshold.
Deterministic. State-gated (CONTEXT_BUILDING only).
Stops when context is sufficient.
"""

from typing import Optional
from cold_strategist.context.context_schema import DecisionContext, Stakes, EmotionalLoad


class QuestionEngine:
    """
    Generates clarifying questions in strict order.
    
    Deterministic progression ensures human input drives context building,
    not algorithmic wandering.
    """
    
    def __init__(self):
        """Initialize the question engine."""
        self.question_order = [
            "domain",
            "stakes",
            "irreversibility",
            "emotional_load",
            "prior_patterns"
        ]
    
    def generate(self, ctx: DecisionContext) -> Optional[str]:
        """
        Generate the next necessary question based on context gaps.
        
        Args:
            ctx: Current decision context
            
        Returns:
            Next clarifying question, or None if context is sufficient
        """
        if ctx.domain is None:
            return (
                "What kind of situation is this? "
                "(relationship, career, conflict, money, identity, other)"
            )
        
        if ctx.stakes is None:
            return (
                "What is the worst realistic outcome if nothing changes? "
                "(And how bad is that?)"
            )
        
        if ctx.irreversibility is None:
            return (
                "If you choose wrong, can this be undone "
                "without lasting damage? (yes/no)"
            )
        
        if ctx.emotional_load is None:
            return (
                "What emotion is strongest right now? "
                "(fear, anger, shame, regret, confusion, something else)"
            )
        
        if not ctx.prior_patterns:
            return (
                "Have you faced something structurally similar before? "
                "(Describe briefly or 'never')"
            )
        
        return None
    
    def has_next_question(self, ctx: DecisionContext) -> bool:
        """Check if more questions are needed."""
        return self.generate(ctx) is not None

