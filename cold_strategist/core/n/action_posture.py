"""
Action Posture - Decision Stance Selection (LOCKED)

Determines posture based on:
- Trajectory (corrosive → abort)
- Confidence (high + urgency → force)
- Emotional load (high → delay)
- Default (conditional with caveats)

Postures:
- "abort": Do not execute. Trajectory too corrosive.
- "force": Execute now. High confidence + high stakes justify speed.
- "delay": Wait. Emotional load or insufficient confidence. Revisit after cooling.
- "conditional": Execute if conditions met. Otherwise re-evaluate.
"""

from typing import List, Dict
from context.context_schema import DecisionContext, EmotionalLoad


class ActionPosture:
    """
    Decides the stance on whether to execute the action.
    
    NOT yes/no. But HOW and WHEN.
    """
    
    def decide_posture(
        self,
        weighted_verdicts: List[Dict],
        ctx: DecisionContext,
        trajectory: str
    ) -> str:
        """
        Determine action posture based on all signals.
        
        Args:
            weighted_verdicts: Weighted minister verdicts
            ctx: Decision context
            trajectory: "aligns" | "neutral" | "corrosive"
            
        Returns:
            "abort" | "force" | "delay" | "conditional"
        """
        # Corrosive trajectory: abort
        if trajectory == "corrosive":
            return "abort"
        
        # High confidence + urgency: force
        if weighted_verdicts:
            top_weight = weighted_verdicts[0]["weight"]
            if top_weight > 0.85 and ctx.time_pressure:
                return "force"
        
        # High emotional load: delay
        if ctx.emotional_load == EmotionalLoad.HIGH:
            return "delay"
        
        # Low confidence: conditional
        if weighted_verdicts and weighted_verdicts[0]["weight"] < 0.6:
            return "conditional"
        
        # Default: conditional
        return "conditional"
    
    def posture_rationale(
        self,
        posture: str,
        trajectory: str,
        ctx: DecisionContext,
        top_weight: float
    ) -> str:
        """
        Generate explanation of posture decision.
        
        Args:
            posture: Selected posture
            trajectory: Trajectory assessment
            ctx: Decision context
            top_weight: Highest weighted verdict score
            
        Returns:
            String rationale
        """
        rationales = {
            "abort": (
                f"ABORT: Long-term trajectory is {trajectory}. "
                "Action locks in deterioration. Do not execute."
            ),
            "force": (
                f"FORCE: Top verdict confidence {int(top_weight*100)}% + time pressure. "
                "Execute now. Delay increases risk."
            ),
            "delay": (
                f"DELAY: Emotional load is high ({ctx.emotional_load.value}). "
                "Cool off for 24-48 hours. Revisit with clearer head."
            ),
            "conditional": (
                f"CONDITIONAL: Top verdict confidence {int(top_weight*100)}%. "
                "Execute only if specific conditions hold. "
                "Otherwise, wait for more information."
            )
        }
        
        return rationales.get(posture, "Unknown posture")
