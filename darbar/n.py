"""
Prime Confidant (N) - The Inner Circle
Sovereign's most trusted advisor and liaison to the council.

N frames the final verdict, ensuring all evidence remains visible
and decision traceability is preserved.
"""

from typing import List, Dict, Any, Optional


class N:
    """
    Prime Confidant - Sovereign's most trusted advisor.
    
    Role: Synthesize council positions into actionable verdict,
    while preserving evidence chain and maintaining transparency.
    """

    def __init__(self):
        """Initialize the Prime Confidant."""
        pass

    def frame_verdict(
        self,
        positions: List[Dict[str, Any]],
        tribunal_judgment: Optional[str],
        goal: str,
    ) -> str:
        """
        Frame final verdict from council positions.
        
        Args:
            positions: List of DebatePosition dicts (minister positions with advice)
            tribunal_judgment: Optional judgment from tribunal
            goal: User's stated goal
        
        Returns:
            Framed verdict with all citations preserved
        """
        lines = [
            "=" * 60,
            "FINAL VERDICT (from N, Sovereign's Inner Circle)",
            "=" * 60,
            "",
        ]

        # Summary of advice
        lines.append(f"GOAL: {goal}")
        lines.append("")

        if positions:
            lines.append("COUNCIL CONSENSUS:")
            for p in positions:
                confidence_bar = "█" * int(p.get("confidence", 0.0) * 10) + "░" * (
                    10 - int(p.get("confidence", 0.0) * 10)
                )
                lines.append(f"\n{p.get('minister', 'unknown').upper()}")
                lines.append(f"  Confidence: [{confidence_bar}] {p.get('confidence', 0.0):.0%}")
                if p.get("advice"):
                    lines.append(f"  Advice: {p['advice']}")
                if p.get("risks"):
                    lines.append(f"  Risks: {', '.join(p['risks'])}")

        # Tribunal input
        if tribunal_judgment:
            lines.append("")
            lines.append("TRIBUNAL ASSESSMENT:")
            for jline in tribunal_judgment.split("\n"):
                lines.append(f"  {jline}")

        # Citation summary
        all_citations = []
        for p in positions:
            all_citations.extend(p.get("citations", []))

        if all_citations:
            lines.append("")
            lines.append("EVIDENCE CHAIN (citations):")
            for cit in all_citations[:5]:  # Show first 5
                lines.append(
                    f"  [{cit.get('book_id')}] {cit.get('chapter_title')} "
                    f"({cit.get('chunk_id')})"
                )
            if len(all_citations) > 5:
                lines.append(f"  ... and {len(all_citations) - 5} more sources")

        # Final recommendation
        lines.append("")
        lines.append("-" * 60)
        lines.append("N'S RECOMMENDATION:")
        lines.append(
            "Proceed with the consensus advice above. "
            "All sources are inspectable via --show-source <chunk_id>."
        )
        lines.append("-" * 60)

        return "\n".join(lines)

    def advise(self, situation: Dict[str, Any]) -> str:
        """
        Provide direct advice to Sovereign on a situation.
        
        Args:
            situation: Situation dict with context, goal, etc.
        
        Returns:
            Direct advice string
        """
        # Placeholder: in real system, this would integrate with retriever + synthesizer
        return "N will provide direct advice once situation analysis is complete."
