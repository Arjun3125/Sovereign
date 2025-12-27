"""
Verdict Formatter - Final N Output (LOCKED)

The ONLY thing the user sees from N synthesis layer.

Clean, direct format:
- VERDICT: What to do (from top-weighted minister)
- DO_NOT: What will fail if ignored
- WHY: Reasoning in 1-2 sentences
- COST: What this costs (opportunity, risk, etc.)
- POSTURE: How to execute (abort/force/delay/conditional)
- ILLUSION: Blind spot flagged (if any)
- TRAJECTORY: Long-term impact (aligns/neutral/corrosive)

Everything else stays internal.
"""

from typing import Dict, List, Optional


class VerdictFormatter:
    """
    Formats N synthesis into final human-readable verdict.
    
    No jargon. No philosophy. Only facts and decisions.
    """
    
    def build_verdict(
        self,
        posture: str,
        top_verdict: Dict,
        illusions: List[str],
        trajectory: str,
        illusion_summary: str,
        trajectory_explanation: str,
        posture_rationale: str
    ) -> Dict:
        """
        Build final verdict from N synthesis.
        
        Args:
            posture: "abort" | "force" | "delay" | "conditional"
            top_verdict: Highest-weighted minister verdict
            illusions: Detected illusions
            trajectory: "aligns" | "neutral" | "corrosive"
            illusion_summary: Human-readable illusion summary
            trajectory_explanation: Human-readable trajectory summary
            posture_rationale: Human-readable posture explanation
            
        Returns:
            Final verdict dict
        """
        return {
            "VERDICT": top_verdict["position"],
            "DO_NOT": self._extract_prohibition(top_verdict),
            "WHY": self._extract_reasoning(top_verdict),
            "COST": self._extract_cost(top_verdict),
            "POSTURE": {
                "stance": posture,
                "rationale": posture_rationale
            },
            "ILLUSION": {
                "detected": len(illusions) > 0,
                "types": illusions,
                "summary": illusion_summary
            },
            "TRAJECTORY": {
                "assessment": trajectory,
                "explanation": trajectory_explanation
            },
            "CONDITIONS": top_verdict.get("conditions", []),
            "EVIDENCE": top_verdict.get("evidence", []),
            "CONFIDENCE": top_verdict["confidence"]
        }
    
    def _extract_prohibition(self, verdict: Dict) -> str:
        """
        Extract the core prohibition from verdict.
        
        Args:
            verdict: Minister verdict dict
            
        Returns:
            Prohibition statement or "—" if none
        """
        warning = verdict.get("warning", "")
        
        if "not" in warning.lower() or "avoid" in warning.lower():
            return warning[:100]  # First 100 chars
        
        return "—"
    
    def _extract_reasoning(self, verdict: Dict) -> str:
        """
        Extract 1-2 sentence reasoning.
        
        Args:
            verdict: Minister verdict dict
            
        Returns:
            Concise reasoning
        """
        evidence = verdict.get("evidence", [])
        
        if evidence:
            return evidence[0][:150]  # First sentence
        
        return "See conditions below."
    
    def _extract_cost(self, verdict: Dict) -> str:
        """
        Extract cost/trade-off statement.
        
        Args:
            verdict: Minister verdict dict
            
        Returns:
            Cost description
        """
        conditions = verdict.get("conditions", [])
        
        if conditions:
            return f"If {conditions[0]}, then proceed. Otherwise: defer."
        
        return "Opportunity cost and exposure to be managed."
    
    def format_for_display(self, verdict: Dict) -> str:
        """
        Format verdict as clean text for display.
        
        Args:
            verdict: Final verdict dict
            
        Returns:
            Formatted string
        """
        lines = []
        
        lines.append("=" * 60)
        lines.append("DECISION VERDICT")
        lines.append("=" * 60)
        
        lines.append(f"\n→ VERDICT: {verdict['VERDICT']}")
        
        if verdict.get("DO_NOT") and verdict["DO_NOT"] != "—":
            lines.append(f"\n⚠ DO NOT: {verdict['DO_NOT']}")
        
        lines.append(f"\n📌 WHY: {verdict['WHY']}")
        
        lines.append(f"\n💰 COST: {verdict['COST']}")
        
        posture = verdict["POSTURE"]
        lines.append(f"\n⚡ POSTURE: {posture['stance'].upper()}")
        lines.append(f"   {posture['rationale']}")
        
        if verdict["ILLUSION"]["detected"]:
            lines.append(f"\n🔍 BLIND SPOT: {verdict['ILLUSION']['summary']}")
        
        trajectory = verdict["TRAJECTORY"]
        lines.append(f"\n📈 TRAJECTORY: {trajectory['assessment'].upper()}")
        lines.append(f"   {trajectory['explanation']}")
        
        if verdict.get("CONDITIONS"):
            lines.append("\n📋 CONDITIONS FOR EXECUTION:")
            for i, cond in enumerate(verdict["CONDITIONS"], 1):
                lines.append(f"   {i}. {cond}")
        
        lines.append(f"\n✓ CONFIDENCE: {int(verdict['CONFIDENCE']*100)}%")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
