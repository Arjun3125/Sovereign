"""
Verdict Formatter - Debate Output to N (LOCKED)

Packages debate results into clean JSON for N synthesis.

Output contains:
- Verdicts (what each minister said)
- Contradictions (structural conflicts found)
- Concessions (partial agreements)
- Dominant risks (top warnings)
- Least damage path (consensus on worst-case mitigation)
- Unresolved tensions (yes/no)

Only output goes to N. All internal debate details stay in debate layer.
"""

from typing import List, Dict, Optional
from dataclasses import asdict
from core.debate.debate_schema import (
    MinisterVerdict,
    Objection,
    Concession,
    DebateRound
)
from core.debate.contradiction_detector import Contradiction


class VerdictFormatter:
    """
    Formats debate output for N synthesis.
    
    Clean JSON. No noise. All critical information present.
    """
    
    def format_debate_output(
        self,
        debate_round: DebateRound,
        contradictions: List[Contradiction],
        dominant_risks: List[str],
        least_damage_path: Optional[str] = None
    ) -> Dict:
        """
        Format complete debate round into N-ready output.
        
        Args:
            debate_round: Complete DebateRound with verdicts, objections, concessions
            contradictions: List of detected contradictions
            dominant_risks: Top warnings across all verdicts
            least_damage_path: If consensus exists, describe minimal-harm path
            
        Returns:
            Dict ready for JSON serialization and N processing
        """
        return {
            "debate_phase": debate_round.phase,
            "verdicts": self._format_verdicts(debate_round.verdicts),
            "objections": self._format_objections(debate_round.objections),
            "concessions": self._format_concessions(debate_round.concessions),
            "contradictions": self._format_contradictions(contradictions),
            "dominant_risks": dominant_risks,
            "least_damage_path": least_damage_path,
            "unresolved_tension": len(contradictions) > 0,
            "summary": self._generate_summary(debate_round, contradictions)
        }
    
    def _format_verdicts(self, verdicts: List[MinisterVerdict]) -> List[Dict]:
        """
        Format minister verdicts for output.
        
        Args:
            verdicts: List of verdicts
            
        Returns:
            List of formatted verdict dicts
        """
        return [
            {
                "minister": v.minister_name,
                "position": v.position,
                "warning": v.warning,
                "verdict_type": v.verdict_type.value,
                "confidence": v.confidence,
                "evidence": v.evidence,
                "conditions": v.conditions
            }
            for v in verdicts
        ]
    
    def _format_objections(self, objections: List[Objection]) -> List[Dict]:
        """
        Format objections for output.
        
        Args:
            objections: List of objections
            
        Returns:
            List of formatted objection dicts
        """
        return [
            {
                "from": o.objector,
                "to": o.target_minister,
                "type": o.objection_type.value,
                "statement": o.statement,
                "severity": o.severity,
                "counter_position": o.counter_position
            }
            for o in objections
        ]
    
    def _format_concessions(self, concessions: List[Concession]) -> List[Dict]:
        """
        Format concessions for output.
        
        Args:
            concessions: List of concessions
            
        Returns:
            List of formatted concession dicts
        """
        return [
            {
                "minister": c.minister_name,
                "concedes_to": c.concedes_to,
                "original_claim": c.original_claim,
                "revised_claim": c.revised_claim,
                "reason": c.reason
            }
            for c in concessions
        ]
    
    def _format_contradictions(self, contradictions: List[Contradiction]) -> List[Dict]:
        """
        Format contradictions for output.
        
        Args:
            contradictions: List of contradictions
            
        Returns:
            List of formatted contradiction dicts
        """
        return [
            {
                "type": c.type,
                "minister_a": c.minister_a,
                "minister_b": c.minister_b,
                "description": c.description,
                "severity": c.severity
            }
            for c in contradictions
        ]
    
    def _generate_summary(
        self,
        debate_round: DebateRound,
        contradictions: List[Contradiction]
    ) -> Dict:
        """
        Generate high-level summary of debate state.
        
        Args:
            debate_round: Complete debate round
            contradictions: Detected contradictions
            
        Returns:
            Summary dict
        """
        verdicts_by_type = {}
        for v in debate_round.verdicts:
            vtype = v.verdict_type.value
            verdicts_by_type[vtype] = verdicts_by_type.get(vtype, 0) + 1
        
        has_consensus = (
            len(verdicts_by_type) == 1
            and "viable" in verdicts_by_type
        )
        
        return {
            "total_ministers": len(debate_round.verdicts),
            "verdict_distribution": verdicts_by_type,
            "consensus_on_viability": has_consensus,
            "objection_count": len(debate_round.objections),
            "concession_count": len(debate_round.concessions),
            "contradiction_count": len(contradictions),
            "high_severity_contradictions": len(
                [c for c in contradictions if c.severity == "high"]
            ),
            "unresolved_tension": len(contradictions) > 0
        }
