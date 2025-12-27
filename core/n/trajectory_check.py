"""
Trajectory Check - Long-Term Alignment Assessment (LOCKED)

Evaluates whether chosen action aligns with or corrodes long-term trajectory.

Returns:
- "aligns": Action compounds positively over time
- "neutral": No long-term trajectory effect
- "corrosive": Action damages long-term position (compounding losses)

Used by N to decide action posture (abort vs. force vs. delay vs. conditional).
"""

from context.context_schema import DecisionContext, Stakes


class TrajectoryChecker:
    """
    Assesses long-term trajectory alignment.
    
    Not about whether action is "good", but whether it compounds
    positively or negatively over time.
    """
    
    def check_trajectory(self, ctx: DecisionContext) -> str:
        """
        Evaluate long-term trajectory impact.
        
        Args:
            ctx: Decision context
            
        Returns:
            "aligns" | "neutral" | "corrosive"
        """
        # Corrosive signals
        if self._is_corrosive(ctx):
            return "corrosive"
        
        # Aligning signals
        if self._is_aligning(ctx):
            return "aligns"
        
        # Default: neutral
        return "neutral"
    
    def _is_corrosive(self, ctx: DecisionContext) -> bool:
        """
        Detect corrosive trajectory patterns.
        
        Corrosive: Irreversible action taken for short-term relief.
        Losses compound; position deteriorates.
        
        Args:
            ctx: Decision context
            
        Returns:
            True if trajectory is corrosive
        """
        # Irreversible action + seeking relief = corrosive
        if ctx.irreversibility and ctx.emotional_load:
            return True
        
        # Existential stakes + high compounding effect = corrosive
        if ctx.stakes == Stakes.EXISTENTIAL and ctx.compounding:
            return True
        
        # High irreversibility + no prior patterns = likely blind decision
        if ctx.irreversibility and len(ctx.prior_patterns) == 0:
            return True
        
        return False
    
    def _is_aligning(self, ctx: DecisionContext) -> bool:
        """
        Detect aligning trajectory patterns.
        
        Aligning: Action reinforces long-term positioning,
        builds optionality, creates compound benefits.
        
        Args:
            ctx: Decision context
            
        Returns:
            True if trajectory is aligning
        """
        # Reversible + builds optionality = aligning
        if not ctx.irreversibility and ctx.domain in ["optionality", "learning"]:
            return True
        
        # High stakes + compounding benefit = aligning
        if ctx.stakes in [Stakes.HIGH, Stakes.EXISTENTIAL] and ctx.compounding:
            # Only if not irreversible (corrosive catches that)
            if not ctx.irreversibility:
                return True
        
        # Repeated pattern + positive outcome history = aligning
        if len(ctx.prior_patterns) > 2:
            return True
        
        return False
    
    def trajectory_explanation(self, trajectory: str, ctx: DecisionContext) -> str:
        """
        Generate explanation of trajectory assessment.
        
        Args:
            trajectory: "aligns" | "neutral" | "corrosive"
            ctx: Decision context
            
        Returns:
            String explanation
        """
        explanations = {
            "aligns": (
                "Long-term position strengthens: "
                "action compounds positively, builds optionality, or reinforces pattern."
            ),
            "neutral": (
                "No clear long-term trajectory impact: "
                "action is isolated or reversible enough to not shape future."
            ),
            "corrosive": (
                "Long-term position deteriorates: "
                "action locks in losses, creates path dependency, or closes options."
            )
        }
        
        return explanations.get(trajectory, "Unknown trajectory")
