"""
Question Gate - Singular Clarifying Question Logic (LOCKED)

Before returning verdict, N checks: Do we need one more question?

Triggers question if:
- Top verdict confidence < 0.6 AND stakes are high
- Key information gap detected
- Illusion pattern suggests clarification needed

Returns either:
- { "mode": "question", "question": "..." }
- { "mode": "verdict", "verdict": {...} }

Questions are SHARP. Single. Designed to unlock insight.
"""

from typing import List, Dict, Optional
from core.debate.debate_schema import MinisterVerdict


class QuestionGate:
    """
    Determines if one final clarifying question is needed.
    
    Before committing to verdict, check if a single question
    would materially change the analysis.
    """
    
    def needs_question(
        self,
        weighted_verdicts: List[Dict],
        ctx,  # DecisionContext
        illusions: List[str]
    ) -> bool:
        """
        Check if a clarifying question would be valuable.
        
        Args:
            weighted_verdicts: Weighted minister verdicts
            ctx: Decision context
            illusions: Detected illusions
            
        Returns:
            True if question gate triggers
        """
        if not weighted_verdicts:
            return True
        
        top_weight = weighted_verdicts[0]["weight"]
        
        # Low confidence + high stakes = ask before acting
        if top_weight < 0.6 and ctx.stakes in ["high", "existential"]:
            return True
        
        # Illusion detected + low consensus = clarify
        if illusions and top_weight < 0.7:
            return True
        
        return False
    
    def build_question(
        self,
        weighted_verdicts: List[Dict],
        ctx,  # DecisionContext
        illusions: List[str]
    ) -> str:
        """
        Build a single sharp clarifying question.
        
        Args:
            weighted_verdicts: Weighted verdicts
            ctx: Decision context
            illusions: Detected illusions
            
        Returns:
            Single question string
        """
        # If ego protection detected, ask about real stakes
        if "ego_protection" in illusions:
            return (
                "If this fails, what exactly are you actually protecting? "
                "(Not what you say, but what you feel.)"
            )
        
        # If scarcity illusion, test patience
        if "scarcity_illusion" in illusions:
            return (
                "What happens if you wait 30 days before deciding? "
                "Does the situation fundamentally change?"
            )
        
        # If emotional distortion, ask for opposite view
        if "emotional_distortion" in illusions:
            return (
                "What would the strongest objection to your position be? "
                "From someone you respect."
            )
        
        # If convergence bias (too much pattern matching), ask for exceptions
        if "convergence_bias" in illusions:
            return (
                "When has this pattern NOT held true? "
                "What made it different?"
            )
        
        # If low confidence across board, ask for minimum certainty
        if weighted_verdicts and weighted_verdicts[0]["weight"] < 0.6:
            return (
                "What is the ONE thing you're most certain about "
                "in this situation?"
            )
        
        # Default: ask for trajectory
        return (
            "In 6 months, will you have moved closer or further "
            "from where you want to be?"
        )
