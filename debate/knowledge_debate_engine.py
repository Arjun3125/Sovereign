"""
Enhanced Debate Engine - Knowledge-Grounded Darbari Mode

Integrates:
- MinisterRetriever: Domain-filtered knowledge access
- MinisterSynthesizer: Grounded advice synthesis
- Tribunal: Escalation logic
- N: Final framing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from core.knowledge.minister_retriever import MinisterRetriever
from core.knowledge.war_aware_rag_retriever import WarAwareRAGRetriever
from core.knowledge.synthesize.minister_synthesizer import MinisterSynthesizer
from darbar.tribunal import Tribunal
from darbar.n import N


@dataclass
class DebatePosition:
    """Single minister's position in the debate."""
    minister: str
    status: str  # "ADVICE" | "STOP" | "NEEDS_CLARIFICATION"
    advice: Optional[str]
    rationale: Optional[str]
    confidence: float
    citations: List[Dict[str, str]]
    risks: List[str]


@dataclass
class DebateProceedings:
    """Complete debate outcome."""
    positions: List[DebatePosition]
    escalated: bool
    tribunal_judgment: Optional[str]
    final_verdict: Optional[str]
    event_id: Optional[str]


class KnowledgeGroundedDebateEngine:
    """
    Orchestrates structured debate between ministers, grounded in retrieved knowledge.
    
    Flow:
    1. Select relevant ministers based on context
    2. For each minister: retrieve knowledge → synthesize advice
    3. Debate: compare positions, identify conflicts
    4. Escalate to tribunal if conflicts exist
    5. N frames final verdict with all evidence visible
    """

    def __init__(
        self,
        retriever: MinisterRetriever,
        synthesizer: MinisterSynthesizer,
        tribunal: Optional[Tribunal] = None,
        n: Optional[N] = None,
    ):
        """
        Args:
            retriever: MinisterRetriever instance (has access to global VectorIndex)
            synthesizer: MinisterSynthesizer instance (has access to LLM)
            tribunal: Tribunal instance for escalation (optional)
            n: Prime Confidant (optional)
        """
        self.retriever = retriever
        self.synthesizer = synthesizer
        self.tribunal = tribunal or Tribunal()
        self.n = n or N()

    def conduct_debate(
        self,
        context: Dict[str, Any],
        state: Dict[str, Any],
        goal: str,
        selected_ministers: Optional[List[str]] = None,
        confidence_threshold: float = 0.65,
        include_audit: bool = False,
    ) -> DebateProceedings:
        """
        Conduct a complete knowledge-grounded debate.

        Args:
            context: Current situation context
            state: Current state (fatigue, resources, etc.)
            goal: User's stated goal (non-negotiable)
            selected_ministers: List of minister names to include (if None, use all)
            confidence_threshold: Min confidence for advice (others ask questions)

        Returns:
            DebateProceedings with all positions, tribunal judgment, final verdict
        """
        if selected_ministers is None:
            selected_ministers = list(self._default_ministers())

        # Step 1: Debate - each minister retrieves and synthesizes
        positions: List[DebatePosition] = []
        for minister in selected_ministers:
            position = self._minister_position(
                minister=minister,
                goal=goal,
                context=context,
                confidence_threshold=confidence_threshold,
                state=state,
                include_audit=include_audit,
            )
            positions.append(position)

        # Step 2: Detect conflicts
        conflicts = self._detect_conflicts(positions)
        escalated = len(conflicts) > 0

        # Step 3: Escalate to tribunal if needed
        tribunal_judgment = None
        if escalated:
            tribunal_judgment = self._escalate_to_tribunal(
                positions=positions,
                conflicts=conflicts,
                goal=goal,
                state=state,
            )

        # Step 4: Frame final verdict via N
        final_verdict = self._frame_final_verdict(
            positions=positions,
            tribunal_judgment=tribunal_judgment,
            goal=goal,
        )

        return DebateProceedings(
            positions=positions,
            escalated=escalated,
            tribunal_judgment=tribunal_judgment,
            final_verdict=final_verdict,
            event_id=None,  # To be filled by caller
        )

    def _minister_position(
        self,
        minister: str,
        goal: str,
        context: Dict[str, Any],
        confidence_threshold: float,
        state: Dict[str, Any],
        include_audit: bool = False,
    ) -> DebatePosition:
        """
        Get single minister's position: retrieve → synthesize → evaluate.
        """
        try:
            # Step 1: Retrieve knowledge for this minister
            mode = state.get("mode") if isinstance(state, dict) else None

            if mode == "war":
                try:
                    war_retriever = WarAwareRAGRetriever(base_retriever=self.retriever)
                    retrieved = war_retriever.retrieve_for_minister(
                        minister_name=minister,
                        query=goal,
                        mode="war",
                        k=5,
                        include_counter=True,
                        include_audit=include_audit,
                    )
                except Exception:
                    # Fallback to base retriever on error
                    retrieved = self.retriever.retrieve_for_minister(
                        minister_name=minister,
                        query=goal,
                        k=5,
                        include_counter=True,
                    )
            else:
                retrieved = self.retriever.retrieve_for_minister(
                    minister_name=minister,
                    query=goal,
                    k=5,
                    include_counter=True,
                )

            # Step 2: Synthesize advice from retrieved knowledge
            synthesis = self.synthesizer.synthesize(
                minister_name=minister,
                goal=goal,
                context=context,
                retrieved=retrieved,
                confidence_threshold=confidence_threshold,
            )

            # Extract position
            status = synthesis.get("status", "ADVICE")
            advice = synthesis.get("advice")
            rationale = synthesis.get("rationale")
            confidence = synthesis.get("confidence", 0.0)
            citations = synthesis.get("citations", [])
            risks = synthesis.get("risks", [])

            return DebatePosition(
                minister=minister,
                status=status,
                advice=advice,
                rationale=rationale,
                confidence=confidence,
                citations=citations,
                risks=risks,
            )

        except Exception as e:
            # Minister unavailable or no knowledge
            return DebatePosition(
                minister=minister,
                status="STOP",
                advice=None,
                rationale=f"Error: {str(e)}",
                confidence=0.0,
                citations=[],
                risks=[],
            )

    def _detect_conflicts(self, positions: List[DebatePosition]) -> List[str]:
        """
        Detect logical conflicts between minister positions.
        
        Simple heuristic: compare advice semantically (in real system, use LLM).
        """
        conflicts = []

        # For now: flag high-risk or low-confidence positions
        for p in positions:
            if p.status == "STOP":
                conflicts.append(f"{p.minister}: blocked (alignment issue)")
            elif p.status == "NEEDS_CLARIFICATION":
                conflicts.append(f"{p.minister}: low confidence, needs clarification")

        return conflicts

    def _escalate_to_tribunal(
        self,
        positions: List[DebatePosition],
        conflicts: List[str],
        goal: str,
        state: Dict[str, Any],
    ) -> str:
        """
        Escalate conflicts to tribunal for sovereign judgment.
        """
        # Format dispute summary
        dispute = {
            "conflicts": conflicts,
            "positions": [
                {
                    "minister": p.minister,
                    "status": p.status,
                    "confidence": p.confidence,
                    "risks": p.risks,
                }
                for p in positions
            ],
            "goal": goal,
            "state": state,
        }

        # Tribunal judgment (placeholder)
        judgment = self.tribunal.escalate(dispute)

        return judgment or "Tribunal: Review positions in context of goal. Proceed with caution."

    def _frame_final_verdict(
        self,
        positions: List[DebatePosition],
        tribunal_judgment: Optional[str],
        goal: str,
    ) -> str:
        """
        Frame final verdict via N, preserving evidence visibility.
        """
        # Collect all ADVICE positions
        advice_positions = [p for p in positions if p.status == "ADVICE"]

        if not advice_positions:
            return f"N's Assessment: No consensual advice reached. {tribunal_judgment or ''}"

        # Synthesize via N
        verdict = self.n.frame_verdict(
            positions=advice_positions,
            tribunal_judgment=tribunal_judgment,
            goal=goal,
        )

        return verdict

    def _default_ministers(self) -> List[str]:
        """Default minister set for debate."""
        return [
            "truth",
            "optionality",
            "power",
            "conflict",
            "diplomacy",
            "psychology",
            "strategy",
        ]
