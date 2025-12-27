"""
Contribution Matrix - Dynamic Minister Relevance Scoring (LOCKED)

Scores how much each minister contributes to analyzing the current context.
Deterministic. Context-driven. No opinion.

Higher score = more relevant to this specific decision.
"""

from context.context_schema import DecisionContext, Stakes, EmotionalLoad
from core.selection.minister_registry import MINISTERS


# ============================================================================
# CONTRIBUTION SCORING
# ============================================================================

class ContributionMatrix:
    """
    Scores how relevant each minister is to the current decision context.
    
    Scoring is purely factual:
    - Domain match: +2
    - Irreversibility detected: +2
    - High emotion: +2
    - High/existential stakes: +2
    - Time pressure: +1
    
    Minimum viable score: 3 (qualifies for selection)
    """
    
    DOMAIN_MATCH_SCORE = 2
    IRREVERSIBILITY_SCORE = 2
    EMOTION_SCORE = 2
    HIGH_STAKES_SCORE = 2
    TIME_PRESSURE_SCORE = 1
    
    MINIMUM_SCORE = 3
    
    def __init__(self):
        """Initialize contribution matrix."""
        self.ministers = MINISTERS
    
    def score_all_ministers(self, ctx: DecisionContext) -> dict:
        """
        Score all ministers based on context.
        
        Args:
            ctx: Decision context
            
        Returns:
            Dict mapping minister name → score
        """
        scores = {}
        
        for minister, domains in self.ministers.items():
            score = self._score_minister(ctx, domains)
            scores[minister] = score
        
        return scores
    
    def _score_minister(self, ctx: DecisionContext, domains: list) -> int:
        """
        Calculate score for a specific minister.
        
        Args:
            ctx: Decision context
            domains: Minister's domain keywords
            
        Returns:
            Integer score
        """
        score = 0
        
        # Domain match
        if ctx.domain and ctx.domain in domains:
            score += self.DOMAIN_MATCH_SCORE
        
        # Irreversibility check
        if ctx.irreversibility and "irreversibility" in domains:
            score += self.IRREVERSIBILITY_SCORE
        
        # High emotional load indicates need for psychology/bias analysis
        if ctx.emotional_load == EmotionalLoad.HIGH:
            if any(kw in domains for kw in ["bias", "emotion", "self-deception"]):
                score += self.EMOTION_SCORE
        
        # High/existential stakes need risk and power analysis
        if ctx.stakes in [Stakes.HIGH, Stakes.EXISTENTIAL]:
            if any(kw in domains for kw in ["ruin", "irreversibility", "tail-risk", "leverage"]):
                score += self.HIGH_STAKES_SCORE
        
        # Time pressure requires timing expertise
        if ctx.time_pressure and "tempo" in domains:
            score += self.TIME_PRESSURE_SCORE
        
        return score
    
    def ministers_above_threshold(self, ctx: DecisionContext) -> list:
        """
        Get all ministers with score >= minimum threshold.
        
        Args:
            ctx: Decision context
            
        Returns:
            List of (minister_name, score) tuples, sorted by score descending
        """
        scores = self.score_all_ministers(ctx)
        
        qualified = [
            (minister, score)
            for minister, score in scores.items()
            if score >= self.MINIMUM_SCORE
        ]
        
        return sorted(qualified, key=lambda x: x[1], reverse=True)
    
    def score_explanation(self, ctx: DecisionContext, minister: str) -> str:
        """
        Generate human-readable explanation of why a minister scored.
        
        Args:
            ctx: Decision context
            minister: Minister name
            
        Returns:
            String explanation
        """
        domains = self.ministers.get(minister, [])
        reasons = []
        
        if ctx.domain and ctx.domain in domains:
            reasons.append(f"domain match ({ctx.domain})")
        
        if ctx.irreversibility and "irreversibility" in domains:
            reasons.append("irreversibility detection")
        
        if ctx.emotional_load == EmotionalLoad.HIGH:
            if any(kw in domains for kw in ["bias", "emotion"]):
                reasons.append(f"high emotional load ({ctx.emotional_load})")
        
        if ctx.stakes in [Stakes.HIGH, Stakes.EXISTENTIAL]:
            if any(kw in domains for kw in ["ruin", "leverage"]):
                reasons.append(f"high/existential stakes ({ctx.stakes})")
        
        if ctx.time_pressure and "tempo" in domains:
            reasons.append("time pressure")
        
        return "; ".join(reasons) if reasons else "below threshold"
