"""
Phase-3: Decision Pipeline Integration

Phase-3 bridges Phase-1 (initial assessment) output into the downstream
decision pipeline (Quick Mode, Normal Mode, War Mode).

Architecture:
- Phase-1 output (status, confidence, decision, actions) → Phase-3 evaluator
- Phase-3 decides: PROCEED to inline decision, ESCALATE to full debate, or REQUEST_MORE_INFO
- Phase-3 output feeds into mode selection (Quick/Normal/War)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal
from cold_strategist.phase1.schema import Phase1Response


@dataclass
class Phase3Assessment:
    """Phase-3 evaluation of Phase-1 output and recommended action."""

    phase1_status: str  # OK, NEEDS_CONTEXT, ERROR
    phase1_confidence: float
    
    # Phase-3 decision
    decision: Literal["PROCEED", "ESCALATE", "REQUEST_MORE_INFO"]
    reasoning: str
    
    # Mode recommendation (if PROCEED)
    recommended_mode: Optional[Literal["quick", "normal", "war"]] = None
    
    # Follow-up actions
    actions: Optional[list] = None
    
    # Metadata
    escalation_reason: Optional[str] = None
    
    def should_proceed_inline(self) -> bool:
        """Check if Phase-1 confidence is high enough for inline decision."""
        return self.decision == "PROCEED"
    
    def should_escalate_to_debate(self) -> bool:
        """Check if should escalate to full debate (Normal/War mode)."""
        return self.decision == "ESCALATE"
    
    def requires_more_context(self) -> bool:
        """Check if more information is needed."""
        return self.decision == "REQUEST_MORE_INFO"


class Phase3Evaluator:
    """
    Evaluate Phase-1 output and make routing decisions.
    
    Decision logic:
    - Phase1 status=ERROR → REQUEST_MORE_INFO (ask user to clarify)
    - Phase1 status=NEEDS_CONTEXT → REQUEST_MORE_INFO (explicitly insufficient)
    - Phase1 status=OK + confidence >= 0.75 → PROCEED (inline decision, Quick mode)
    - Phase1 status=OK + confidence >= 0.5 → ESCALATE (full debate, Normal mode)
    - Phase1 status=OK + confidence < 0.5 → ESCALATE (conservative; use debate)
    """
    
    CONFIDENCE_THRESHOLD_PROCEED = 0.75
    CONFIDENCE_THRESHOLD_ESCALATE = 0.5
    
    def evaluate(self, phase1_resp: Phase1Response) -> Phase3Assessment:
        """
        Evaluate Phase-1 response and produce routing decision.
        
        Args:
            phase1_resp: Phase1Response from LLM
            
        Returns:
            Phase3Assessment with decision and reasoning
        """
        
        # Case 1: Phase1 encountered an error
        if phase1_resp.status == "ERROR":
            return Phase3Assessment(
                phase1_status="ERROR",
                phase1_confidence=0.0,
                decision="REQUEST_MORE_INFO",
                reasoning="Phase-1 encountered a parsing or processing error. Cannot proceed.",
                escalation_reason="Phase-1 error",
            )
        
        # Case 2: Phase1 needs more context
        if phase1_resp.status == "NEEDS_CONTEXT":
            actions = [{"type": a.type, "description": a.description} for a in (phase1_resp.actions or [])]
            return Phase3Assessment(
                phase1_status="NEEDS_CONTEXT",
                phase1_confidence=phase1_resp.confidence,
                decision="REQUEST_MORE_INFO",
                reasoning=f"Phase-1 assessment: {phase1_resp.reasoning}",
                actions=actions,
                escalation_reason="Insufficient context from user",
            )
        
        # Case 3: Phase1 is OK; decide based on confidence
        if phase1_resp.status == "OK":
            if phase1_resp.confidence >= self.CONFIDENCE_THRESHOLD_PROCEED:
                # High confidence: use Quick mode (inline decision)
                return Phase3Assessment(
                    phase1_status="OK",
                    phase1_confidence=phase1_resp.confidence,
                    decision="PROCEED",
                    reasoning=f"High confidence ({phase1_resp.confidence:.2%}) Phase-1 assessment. Proceeding with Quick mode synthesis.",
                    recommended_mode="quick",
                )
            elif phase1_resp.confidence >= self.CONFIDENCE_THRESHOLD_ESCALATE:
                # Medium confidence: escalate to Normal mode (full debate)
                return Phase3Assessment(
                    phase1_status="OK",
                    phase1_confidence=phase1_resp.confidence,
                    decision="ESCALATE",
                    reasoning=f"Medium confidence ({phase1_resp.confidence:.2%}) Phase-1 assessment. Escalating to full debate.",
                    recommended_mode="normal",
                    escalation_reason="Medium confidence requires debate",
                )
            else:
                # Low confidence: conservative escalation
                return Phase3Assessment(
                    phase1_status="OK",
                    phase1_confidence=phase1_resp.confidence,
                    decision="ESCALATE",
                    reasoning=f"Low confidence ({phase1_resp.confidence:.2%}) Phase-1 assessment. Conservative escalation to full debate.",
                    recommended_mode="normal",
                    escalation_reason="Low confidence; debate recommended",
                )
        
        # Fallback (should not reach)
        return Phase3Assessment(
            phase1_status=phase1_resp.status,
            phase1_confidence=phase1_resp.confidence,
            decision="REQUEST_MORE_INFO",
            reasoning="Unknown Phase-1 status; requesting clarification.",
        )


def apply_phase3_routing(
    phase1_resp: Phase1Response,
    evaluator: Optional[Phase3Evaluator] = None
) -> tuple[Phase3Assessment, Optional[str]]:
    """
    Apply Phase-3 evaluation to Phase-1 output and return routing decision.
    
    Args:
        phase1_resp: Phase1Response from Phase-1 LLM
        evaluator: Phase3Evaluator (uses default if None)
        
    Returns:
        Tuple of (Phase3Assessment, mode_override)
        mode_override: "quick", "normal", "war", or None if REQUEST_MORE_INFO
    """
    if evaluator is None:
        evaluator = Phase3Evaluator()
    
    assessment = evaluator.evaluate(phase1_resp)
    
    mode_override = None
    if assessment.should_proceed_inline():
        mode_override = assessment.recommended_mode or "quick"
    elif assessment.should_escalate_to_debate():
        mode_override = assessment.recommended_mode or "normal"
    # If REQUEST_MORE_INFO, mode_override stays None
    
    return assessment, mode_override
