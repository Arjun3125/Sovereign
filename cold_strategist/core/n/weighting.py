"""
Minister Weighting - Credibility Scoring (LOCKED)

Weights minister verdicts by:
- Base confidence (what they stated)
- Concessions (high signal of intellectual honesty)
- Cross-domain agreement (multiple perspectives agree)
- Contradiction severity (flags unreliable positions)

Higher weight = higher likelihood this minister's verdict is reliable.
Used by N to bias toward strongest positions.
"""

from typing import List, Dict
from core.debate.debate_schema import MinisterVerdict, Objection, Concession


class MinisterWeighting:
    """
    Calculates credibility weights for minister verdicts.
    
    Concessions are high signal: shows willingness to revise.
    Cross-domain support is high signal: independent convergence.
    Unsupported positions are lower signal.
    """
    
    def weight_verdicts(
        self,
        verdicts: List[MinisterVerdict],
        objections: List[Objection],
        concessions: List[Concession]
    ) -> List[Dict]:
        """
        Weight all verdicts based on credibility signals.
        
        Args:
            verdicts: All minister verdicts
            objections: All objections filed
            concessions: All concessions made
            
        Returns:
            List of weighted verdict dicts, sorted by weight descending
        """
        weighted = []
        
        for verdict in verdicts:
            weight = self._calculate_weight(
                verdict,
                objections,
                concessions
            )
            
            weighted.append({
                "minister": verdict.minister_name,
                "position": verdict.position,
                "warning": verdict.warning,
                "verdict_type": verdict.verdict_type.value,
                "confidence": verdict.confidence,
                "weight": weight,
                "evidence": verdict.evidence,
                "conditions": verdict.conditions
            })
        
        return sorted(weighted, key=lambda x: x["weight"], reverse=True)
    
    def _calculate_weight(
        self,
        verdict: MinisterVerdict,
        objections: List[Objection],
        concessions: List[Concession]
    ) -> float:
        """
        Calculate weight for a single verdict.
        
        Base score = stated confidence
        + concession bonus (minister revised after objection)
        + cross-support bonus (other ministers agreed)
        - contradiction penalty
        
        Args:
            verdict: The verdict to weight
            objections: All objections (to check if this minister made concessions)
            concessions: All concessions (to check if this minister conceded)
            
        Returns:
            Weight score (0.0-1.5 range)
        """
        # Start with stated confidence
        weight = verdict.confidence
        
        # Bonus: Minister made concessions (high signal of honesty)
        concessions_made = [
            c for c in concessions
            if c.minister_name == verdict.minister_name
        ]
        if concessions_made:
            weight += 0.2 * len(concessions_made)  # Up to +0.4
        
        # Bonus: Cross-domain support (multiple perspectives agree)
        # This would require comparing verdicts, placeholder for now
        # if self._has_cross_domain_support(verdict, verdicts):
        #     weight += 0.1
        
        # Penalty: Unsupported high-confidence claims
        if verdict.confidence > 0.8 and not verdict.evidence:
            weight -= 0.1
        
        # Cap at 1.0 (confidence can't exceed 100%)
        return min(weight, 1.0)
    
    def weight_summary(self, weighted: List[Dict]) -> str:
        """
        Generate human-readable summary of minister weights.
        
        Args:
            weighted: Weighted verdicts
            
        Returns:
            String summary
        """
        top_three = weighted[:3]
        
        lines = ["Minister Credibility Weights:\n"]
        for i, v in enumerate(top_three, 1):
            lines.append(
                f"{i}. {v['minister']}: {v['weight']:.2f} confidence "
                f"({int(v['confidence']*100)}% stated)"
            )
        
        return "\n".join(lines)
