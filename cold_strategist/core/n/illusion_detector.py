"""
Illusion Detector - Personal Blind Spot Detection (LOCKED)

Detects cognitive distortions in the human's stated situation:

- Emotional Distortion: High emotion + urgent framing
- Ego Protection: Language patterns indicating identity defense
- Scarcity Illusion: "Last chance" or "now or never" thinking
- Confirmation Bias: Pattern hunting to prove pre-existing belief

Returns flagged illusions for N to surface in verdict.
"""

from context.context_schema import DecisionContext, EmotionalLoad
from typing import Optional, List


class IllusionDetector:
    """
    Detects cognitive distortions in human decision-making.
    
    Not moral judgment. Only pattern detection.
    Surfaces them so they can be accounted for in analysis.
    """
    
    SCARCITY_KEYWORDS = [
        "last chance",
        "now or never",
        "window closing",
        "urgency",
        "deadline",
        "expired",
        "only chance",
        "limited time"
    ]
    
    EGO_KEYWORDS = [
        "prove",
        "show them",
        "prove i was right",
        "vindicate",
        "deserve",
        "owed",
        "justice",
        "they were wrong"
    ]
    
    RELIEF_KEYWORDS = [
        "finally",
        "at last",
        "escape",
        "end this",
        "be free",
        "relief",
        "over"
    ]
    
    def detect_illusions(
        self,
        ctx: DecisionContext
    ) -> List[str]:
        """
        Scan context for detected illusions.
        
        Args:
            ctx: Decision context
            
        Returns:
            List of detected illusions (empty if none found)
        """
        illusions = []
        
        # Emotional distortion
        if ctx.emotional_load == EmotionalLoad.HIGH:
            illusions.append("emotional_distortion")
        
        # Ego protection
        ego_detected = self._detect_ego_protection(ctx.raw_input)
        if ego_detected:
            illusions.append("ego_protection")
        
        # Scarcity illusion
        scarcity_detected = self._detect_scarcity_illusion(ctx.raw_input)
        if scarcity_detected:
            illusions.append("scarcity_illusion")
        
        # Convergence illusion (all evidence points to one answer)
        if ctx.prior_patterns and len(ctx.prior_patterns) > 3:
            illusions.append("convergence_bias")
        
        # Fatigue-driven decisions
        if ctx.fatigue:
            illusions.append("decision_fatigue")
        
        return illusions
    
    def _detect_ego_protection(self, raw_input: str) -> bool:
        """
        Detect ego-driven language.
        
        Args:
            raw_input: Raw decision context
            
        Returns:
            True if ego-protection language found
        """
        raw_lower = raw_input.lower()
        
        for keyword in self.EGO_KEYWORDS:
            if keyword in raw_lower:
                return True
        
        return False
    
    def _detect_scarcity_illusion(self, raw_input: str) -> bool:
        """
        Detect scarcity/deadline framing.
        
        Args:
            raw_input: Raw decision context
            
        Returns:
            True if scarcity language found
        """
        raw_lower = raw_input.lower()
        
        for keyword in self.SCARCITY_KEYWORDS:
            if keyword in raw_lower:
                return True
        
        return False
    
    def _detect_relief_seeking(self, raw_input: str) -> bool:
        """
        Detect relief/escape motivation.
        
        Args:
            raw_input: Raw decision context
            
        Returns:
            True if relief language found
        """
        raw_lower = raw_input.lower()
        
        for keyword in self.RELIEF_KEYWORDS:
            if keyword in raw_lower:
                return True
        
        return False
    
    def illusion_summary(self, illusions: List[str]) -> str:
        """
        Generate human-readable summary of detected illusions.
        
        Args:
            illusions: List of detected illusion types
            
        Returns:
            String summary
        """
        if not illusions:
            return "None detected"
        
        descriptions = {
            "emotional_distortion": "High emotion may be clouding judgment",
            "ego_protection": "Some language suggests identity is at stake",
            "scarcity_illusion": "Time-pressure framing may be distorting stakes",
            "convergence_bias": "Pattern repetition may create false consensus",
            "decision_fatigue": "Fatigue detected; consider delaying",
        }
        
        summary_lines = [
            descriptions.get(ill, ill) for ill in illusions
        ]
        
        return "; ".join(summary_lines)
