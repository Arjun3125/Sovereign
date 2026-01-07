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
from core.orchestrator.truth_audit import TruthAudit
 
from datetime import datetime

# Telemetry (best-effort)
try:
    from core.telemetry.store import TelemetryStore
    from core.telemetry.models import MinisterEvent
    from core.telemetry.ids import uid
    telemetry_store = TelemetryStore()
except Exception:
    telemetry_store = None


@dataclass
class DebateTurn:
    """Single turn in auditable debate transcript (STRUCTURED ONLY, NO NARRATIVE)."""
    minister: str
    stance: str  # "ADVANCE" | "DELAY" | "AVOID" | "CONDITIONAL" | "NEEDS_DATA" | "ABSTAIN" | "STOP"
    justification: str  # Doctrine references only, no narrative
    unique_doctrines: int  # COUNT of unique doctrine IDs (not duplicates)
    constraints: List[str]
    risks: List[str]
    confidence: float
    citations: List[Dict[str, str]]
    violations: List[str]  # Truth only: factual violations


@dataclass
class ConflictEvent:
    """Represents a detected conflict between ministers (ISSUE 6 FIX)."""
    conflict_type: str  # "STANCE_CONFLICT" | "VETO_CONFLICT" | "FACTUAL_UNCERTAINTY" | "IRREVERSIBILITY_CONFLICT"
    severity: str  # "LOW" | "MEDIUM" | "HIGH"
    parties: List[str]  # Ministers involved
    reason: str  # Why this conflict matters


@dataclass
class TribunalVerdict:
    """Structured Tribunal verdict (ISSUE 5 FIX)."""
    decision: str  # "ALLOW_WITH_CONSTRAINTS" | "DELAY_PENDING_DATA" | "ESCALATE" | "ABORT" | "SILENCE"
    constraints: List[str]
    reasoning: str
    required_data: List[str]  # If DELAY_PENDING_DATA


@dataclass
class DebatePosition:
    """Single minister's position (HARDENED - structured, no prose)."""
    minister: str
    stance: str  # ADVANCE|DELAY|AVOID|CONDITIONAL|NEEDS_DATA|ABSTAIN|STOP
    justification: str  # Citations only: "Doctrine X, Doctrine Y; because..."
    unique_doctrines: int  # Count of unique doctrine IDs
    constraints: List[str]
    risks: List[str]
    confidence: float
    citations: List[Dict[str, str]]
    violations: List[str] = None  # Truth minister violations


@dataclass
class DebateProceedings:
    """Complete debate outcome."""
    turns: List[DebateTurn]
    positions: List[DebatePosition]
    conflicts: List[ConflictEvent]  # Structured conflict events (ISSUE 6)
    hard_veto: bool
    escalated: bool
    tribunal_verdict: Optional[TribunalVerdict]  # Structured (ISSUE 5)
    final_verdict: Optional[str]
    event_id: Optional[str]


class KnowledgeGroundedDebateEngine:
    """
    Orchestrates structured debate between ministers, grounded in retrieved knowledge.
    
    HARDENED: Stance-based, schema-enforced, hard-veto aware.
    
    Flow:
    1. Select relevant ministers based on context
    2. For each minister: retrieve knowledge → synthesize with schema validation
    3. Detect hard-veto (Risk/Truth/Optionality blocking)
    4. If hard-veto: escalate immediately
    5. Detect stance-based conflicts
    6. Escalate to tribunal if conflicts
    7. N frames (constrained) final verdict
    """
    
    # Hard-veto ministers: must be heard before proceeding
    HARD_VETO_MINISTERS = {"risk", "truth", "optionality"}
    
    # Allowed stances (LLM must output one of these only)
    ALLOWED_STANCES = {"ADVANCE", "DELAY", "AVOID", "CONDITIONAL"}

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
            DebateProceedings with auditable transcript, positions, conflicts, verdict
        """
        # Generate a stable decision identifier for this debate (session-scoped)
        try:
            from core.telemetry.ids import uid as _uid
            decision_id = _uid()
        except Exception:
            decision_id = None

        if selected_ministers is None:
            selected_ministers = list(self._default_ministers())

        # Step 1: Debate - each minister retrieves and synthesizes (with schema validation)
        positions: List[DebatePosition] = []
        turns: List[DebateTurn] = []
        hard_veto_triggered = False
        
        for minister in selected_ministers:
            position = self._minister_position(
                minister=minister,
                goal=goal,
                context=context,
                confidence_threshold=confidence_threshold,
                state=state,
                include_audit=include_audit,
                decision_id=decision_id,
            )
            
            # Validate stance (HARDENING FIX #1)
            if position.stance not in self.ALLOWED_STANCES:
                position.stance = "CONDITIONAL"  # Downgrade invalid stances
            
            positions.append(position)
            
            # Create auditable turn
            turn = DebateTurn(
                minister=minister,
                stance=position.stance,
                justification=position.justification,
                unique_doctrines=position.unique_doctrines,
                constraints=position.constraints,
                risks=position.risks,
                confidence=position.confidence,
                citations=position.citations,
                violations=position.violations or [],
            )
            turns.append(turn)
            
            # Check for hard-veto (HARDENING FIX #3)
            if minister in self.HARD_VETO_MINISTERS and position.stance == "AVOID":
                hard_veto_triggered = True

        # Step 2: Detect real conflicts (ISSUE 6 FIX)
        conflicts = self._detect_conflicts(positions)
        
        # Step 3: Escalate to tribunal if conflicts or hard-veto (ISSUE 5 FIX)
        tribunal_verdict: Optional[TribunalVerdict] = None
        escalated = False
        
        if hard_veto_triggered or conflicts:
            tribunal_verdict = self._escalate_to_tribunal(
                conflicts=conflicts,
                positions=positions,
            )
            escalated = True

        # Step 4: Frame final verdict via N (CONSTRAINED - ISSUE 5 FIX)
        final_verdict = self._frame_final_verdict(
            positions=positions,
            tribunal_verdict=tribunal_verdict,
            hard_veto=hard_veto_triggered,
        )

        return DebateProceedings(
            turns=turns,
            positions=positions,
            conflicts=conflicts,
            hard_veto=hard_veto_triggered,
            escalated=escalated,
            tribunal_verdict=tribunal_verdict,
            final_verdict=final_verdict,
            event_id=decision_id,
        )

    def _minister_position(
        self,
        minister: str,
        goal: str,
        context: Dict[str, Any],
        confidence_threshold: float,
        state: Dict[str, Any],
        include_audit: bool = False,
        decision_id: str = None,
    ) -> DebatePosition:
        """
        HARDENED OUTPUT: No narrative, structured YAML only, dedup checked.
        
        Issues fixed:
        1. No role-playing language
        2. Deduplication of doctrines
        3. Explicit NEEDS_DATA/ABSTAIN/STOP status
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
                        decision_id=decision_id,
                    )
                except Exception:
                    retrieved = self.retriever.retrieve_for_minister(
                        minister_name=minister,
                        query=goal,
                        k=5,
                        include_counter=True,
                        decision_id=decision_id,
                    )
            else:
                retrieved = self.retriever.retrieve_for_minister(
                    minister_name=minister,
                    query=goal,
                    k=5,
                    include_counter=True,
                    decision_id=decision_id,
                )

            # ISSUE 3: Check for "no doctrine" condition early
            if not retrieved or len(retrieved) == 0:
                return DebatePosition(
                    minister=minister,
                    stance="NEEDS_DATA",
                    justification="No doctrine available in knowledge base",
                    unique_doctrines=0,
                    constraints=[],
                    risks=["insufficient_grounding"],
                    confidence=0.0,
                    citations=[],
                    violations=[],
                )

            # Step 2: Synthesize advice from retrieved knowledge
            synthesis = self.synthesizer.synthesize(
                minister_name=minister,
                goal=goal,
                context=context,
                retrieved=retrieved,
                confidence_threshold=confidence_threshold,
            )

            # If synthesizer returned nothing or invalid, discard and STOP
            if not synthesis or not isinstance(synthesis, dict):
                return DebatePosition(
                    minister=minister,
                    stance="STOP",
                    justification="Validation failed or empty synthesis",
                    unique_doctrines=0,
                    constraints=[],
                    risks=["validation_failed"],
                    confidence=0.0,
                    citations=[],
                    violations=[],
                )

            # Expected new schema: justification is a list of {doctrine_id, reason}
            # Backwards-compatible: accept string justification as fallback
            try:
                # Extract stance and validate permitted values
                stance = synthesis.get("stance", "CONDITIONAL")
                if stance not in self.ALLOWED_STANCES and stance not in {"NEEDS_DATA", "ABSTAIN", "STOP"}:
                    stance = "CONDITIONAL"

                # Justification handling: list -> build sanitized string, compute unique doctrines
                justification_field = synthesis.get("justification", "")
                citations = synthesis.get("citations", []) or []

                # Normalize citations to list
                if not isinstance(citations, list):
                    citations = []

                # If justification is list (new schema), compose text and compute unique ids
                unique_doctrine_ids = set()
                if isinstance(justification_field, list):
                    parts = []
                    for j in justification_field:
                        did = j.get("doctrine_id")
                        reason = j.get("reason", "")
                        if did:
                            unique_doctrine_ids.add(did)
                        parts.append(f"{did}: {reason}" if did else reason)
                    justification = "; ".join(parts)
                else:
                    # Fallback: sanitize string justification
                    justification = self._sanitize_justification(str(justification_field or ""))
                    # derive unique ids from citations if present
                    doctrine_ids = [c.get("doctrine_id") for c in citations if c.get("doctrine_id")]
                    unique_doctrine_ids = set(doctrine_ids)

                unique_count = len(unique_doctrine_ids)

                # Confidence
                confidence = synthesis.get("confidence", 0.0)
                if not isinstance(confidence, (int, float)):
                    confidence = 0.0

                # Penalize low diversity
                if unique_count < 2 and confidence > 0.6:
                    confidence = max(0.4, confidence - 0.2)

                constraints = synthesis.get("constraints", []) or []
                if not isinstance(constraints, list):
                    constraints = []

                risks = synthesis.get("risks", []) or []
                if not isinstance(risks, list):
                    risks = []

                # Truth minister: extract violations and enforce STOP
                violations = []
                if minister.lower() == "truth":
                    violations = synthesis.get("violations", []) or []
                    if not isinstance(violations, list):
                        violations = []
                    if violations:
                        stance = "STOP"

            except Exception:
                return DebatePosition(
                    minister=minister,
                    stance="STOP",
                    justification="Synthesis parsing error",
                    unique_doctrines=0,
                    constraints=[],
                    risks=["parsing_error"],
                    confidence=0.0,
                    citations=[],
                    violations=[],
                )

            position = DebatePosition(
                minister=minister,
                stance=stance,
                justification=justification,
                unique_doctrines=unique_count,
                constraints=constraints,
                risks=risks,
                confidence=confidence,
                citations=citations,
                violations=violations,
            )

            # War Mode: telemetry logging (best-effort)
            try:
                if telemetry_store is not None and mode == "war":
                    ts = datetime.utcnow()
                    telemetry_store.append(
                        "minister_events",
                        MinisterEvent(
                            id=uid(),
                            timestamp=ts,
                            decision_id=decision_id,
                            minister=minister,
                            stance=stance,
                            confidence=float(confidence or 0.0),
                            key_points=[justification or ""],
                            rag_refs=unique_doctrine_ids,
                        ),
                    )
            except Exception:
                pass
            
            return position

        except Exception as e:
            # Minister unavailable or error
            return DebatePosition(
                minister=minister,
                stance="ABSTAIN",
                justification=f"Error: {str(e)[:100]}",
                unique_doctrines=0,
                constraints=[],
                risks=["retrieval_error"],
                confidence=0.0,
                citations=[],
                violations=[],
            )

    def _sanitize_justification(self, text: str) -> str:
        """Remove narrative tone, keep only doctrine references and facts."""
        # Strip common narrative phrases
        narrative_phrases = [
            "I firmly believe",
            "I respectfully",
            "I concur",
            "I disagree",
            "honorable",
            "members of the council",
            "I must",
            "I strongly",
        ]
        result = text
        for phrase in narrative_phrases:
            result = result.replace(phrase, "").replace(phrase.capitalize(), "")
        # Clean up extra whitespace
        result = " ".join(result.split()).strip()
        return result

    def _detect_conflicts(self, positions: List[DebatePosition]) -> List[ConflictEvent]:
        """
        ISSUE 6 FIX: Detect structured conflict events by TYPE, not confidence gap.
        
        Conflict types:
        - STANCE_CONFLICT: ADVANCE vs AVOID (direct opposition)
        - VETO_CONFLICT: STOP from critical minister
        - FACTUAL_UNCERTAINTY: Truth minister violations
        - IRREVERSIBILITY_CONFLICT: Risk minister + high consequence
        """
        conflicts: List[ConflictEvent] = []
        stances_by_minister = {}
        truth_violations = []

        # Group ministers by stance
        for p in positions:
            stances_by_minister.setdefault(p.stance, []).append(p.minister)
            if p.violations:
                truth_violations.extend(p.violations)

        # Conflict 1: STANCE_CONFLICT (ADVANCE vs AVOID, both high conf)
        if "ADVANCE" in stances_by_minister and "AVOID" in stances_by_minister:
            advance_positions = [p for p in positions if p.stance == "ADVANCE"]
            avoid_positions = [p for p in positions if p.stance == "AVOID"]
            advance_conf = max([p.confidence for p in advance_positions], default=0)
            avoid_conf = max([p.confidence for p in avoid_positions], default=0)
            
            if advance_conf > 0.65 and avoid_conf > 0.65:
                conflicts.append(ConflictEvent(
                    conflict_type="STANCE_CONFLICT",
                    severity="HIGH",
                    parties=[p.minister for p in advance_positions] + [p.minister for p in avoid_positions],
                    reason=f"Direct opposition: {[p.minister for p in advance_positions]} (ADVANCE {advance_conf:.0%}) vs {[p.minister for p in avoid_positions]} (AVOID {avoid_conf:.0%})",
                ))

        # Conflict 2: VETO_CONFLICT (STOP from Risk/Truth/Optionality)
        stop_positions = [p for p in positions if p.stance == "STOP"]
        for stop_pos in stop_positions:
            if stop_pos.minister in self.HARD_VETO_MINISTERS and stop_pos.confidence > 0.6:
                conflicts.append(ConflictEvent(
                    conflict_type="VETO_CONFLICT",
                    severity="HIGH",
                    parties=[stop_pos.minister],
                    reason=f"Hard veto from {stop_pos.minister} (confidence {stop_pos.confidence:.0%})",
                ))

        # Conflict 3: FACTUAL_UNCERTAINTY (Truth violations detected)
        if truth_violations:
            conflicts.append(ConflictEvent(
                conflict_type="FACTUAL_UNCERTAINTY",
                severity="MEDIUM",
                parties=["truth"],
                reason=f"Fact violations: {'; '.join(truth_violations[:3])}",
            ))

        # Conflict 4: IRREVERSIBILITY_CONFLICT (Risk minister warning on high-risk action)
        risk_position = next((p for p in positions if p.minister == "risk"), None)
        if risk_position and risk_position.stance in {"DELAY", "AVOID"}:
            advance_positions = [p for p in positions if p.stance == "ADVANCE" and p.confidence > 0.7]
            if advance_positions and "irreversible" in str(risk_position.risks).lower():
                conflicts.append(ConflictEvent(
                    conflict_type="IRREVERSIBILITY_CONFLICT",
                    severity="HIGH",
                    parties=["risk"] + [p.minister for p in advance_positions],
                    reason="Risk minister warns irreversibility, but advance positions exist",
                ))

        return conflicts

    def _escalate_to_tribunal(
        self,
        conflicts: List[ConflictEvent],
        positions: List[DebatePosition],
    ) -> TribunalVerdict:
        """
        ISSUE 5 FIX: Return structured tribunal verdict with decision + constraints.
        
        Decision types:
        - ALLOW_WITH_CONSTRAINTS: Majority supports, but add constraints
        - DELAY_PENDING_DATA: Factual uncertainty, need more data
        - ESCALATE: Veto conflict or irreversibility detected
        - ABORT: Hard-veto from critical minister
        - SILENCE: Tribunal recommends no action
        """
        constraints = []
        required_data = []
        decision = "ALLOW_WITH_CONSTRAINTS"
        reasoning = []

        # Map conflict types to decisions
        for conflict in conflicts:
            if conflict.conflict_type == "VETO_CONFLICT":
                decision = "ESCALATE"
                reasoning.append(f"Veto from {conflict.parties[0]}: {conflict.reason}")
                
            elif conflict.conflict_type == "FACTUAL_UNCERTAINTY":
                decision = "DELAY_PENDING_DATA"
                required_data.extend(["fact-check on key claims", "secondary sources"])
                reasoning.append(f"Truth violations detected: {conflict.reason}")
                
            elif conflict.conflict_type == "IRREVERSIBILITY_CONFLICT":
                decision = "ESCALATE"
                constraints.append("Cannot reverse this action once taken; escalate for sign-off")
                reasoning.append(f"Irreversibility risk: {conflict.reason}")
                
            elif conflict.conflict_type == "STANCE_CONFLICT":
                if len(conflict.parties) > 2:
                    decision = "DELAY_PENDING_DATA"
                    constraints.append("Request clarification from parties")
                    required_data.append("Joint position from conflicting ministers")
                reasoning.append(f"Stance conflict among {len(conflict.parties)} parties")

        # Check for hard veto
        hard_veto_positions = [p for p in positions if p.minister in self.HARD_VETO_MINISTERS and p.stance == "STOP" and p.confidence > 0.6]
        if hard_veto_positions:
            decision = "SILENCE"
            reasoning.append(f"Hard veto from {hard_veto_positions[0].minister}: cannot proceed")

        # Check consensus (no conflicts, high confidence majority)
        if not conflicts:
            advance_positions = [p for p in positions if p.stance == "ADVANCE" and p.confidence > 0.65]
            if len(advance_positions) >= len(positions) * 0.66:  # 2/3 majority
                decision = "ALLOW_WITH_CONSTRAINTS"
                constraints.append("Proceed with caution; monitor outcomes")
                reasoning.append("Consensus-based approval (2/3 majority)")
            else:
                decision = "DELAY_PENDING_DATA"
                reasoning.append("Insufficient consensus; request clarification")

        return TribunalVerdict(
            decision=decision,
            constraints=constraints,
            reasoning=" | ".join(reasoning) if reasoning else "Standard tribunal review",
            required_data=required_data
        )

    def _frame_final_verdict(
        self,
        positions: List[DebatePosition],
        tribunal_verdict: Optional[TribunalVerdict],
        hard_veto: bool = False,
    ) -> str:
        """
        ISSUE 5 FIX: Frame final verdict via N (CONSTRAINED).
        
        N may only:
        - ALLOW_WITH_CONSTRAINTS: Summarize consensus + list constraints
        - DELAY_PENDING_DATA: Request required data + list items
        - ESCALATE: Surface for Sovereign review
        - SILENCE: Recommend no action
        - ABORT: Block action (rare)
        
        N must NEVER introduce strategy or narrative.
        """
        # If tribunal verdict exists, apply its decision
        if tribunal_verdict:
            if tribunal_verdict.decision == "SILENCE":
                return f"Tribunal verdict: SILENCE. {tribunal_verdict.reasoning}"
            
            elif tribunal_verdict.decision == "DELAY_PENDING_DATA":
                data_list = ", ".join(tribunal_verdict.required_data) if tribunal_verdict.required_data else "clarification"
                return f"Tribunal verdict: DELAY_PENDING_DATA. Required: {data_list}. {tribunal_verdict.reasoning}"
            
            elif tribunal_verdict.decision == "ESCALATE":
                constraints_str = "; ".join(tribunal_verdict.constraints) if tribunal_verdict.constraints else "none"
                return f"Tribunal verdict: ESCALATE for Sovereign review. Constraints: {constraints_str}. {tribunal_verdict.reasoning}"
            
            elif tribunal_verdict.decision == "ABORT":
                return f"Tribunal verdict: ABORT. Cannot proceed. {tribunal_verdict.reasoning}"
            
            elif tribunal_verdict.decision == "ALLOW_WITH_CONSTRAINTS":
                constraints_str = "; ".join(tribunal_verdict.constraints) if tribunal_verdict.constraints else "proceed with caution"
                return f"Tribunal verdict: ALLOW_WITH_CONSTRAINTS. {constraints_str}. {tribunal_verdict.reasoning}"
        
        # If hard-veto triggered, enforce silence
        if hard_veto:
            return "Hard veto from Risk/Truth/Optionality. Tribunal recommends SILENCE."
        
        # Fallback: Consensus detection without tribunal (2/3 rule for N)
        advance_positions = [p for p in positions if p.stance == "ADVANCE" and p.confidence > 0.65]
        if len(advance_positions) >= len(positions) * 0.66:
            all_constraints = []
            for p in positions:
                all_constraints.extend(p.constraints)
            
            if all_constraints:
                constraints_str = "; ".join(set(all_constraints))
                return f"Consensus to proceed with constraints: {constraints_str}"
            else:
                return "Consensus to proceed. Conditions met."
        
        # No consensus - surface disagreement, request clarification
        stance_counts = {}
        for p in positions:
            stance_counts.setdefault(p.stance, []).append(p.minister)
        
        if len(stance_counts) > 1:
            stances_str = ", ".join(f"{s}({len(ms)})" for s, ms in stance_counts.items())
            return f"Disagreement: {stances_str}. Request clarification from Sovereign."
        
        return "Tribunal: Further review required."
        
        # Fallback
        return f"Council unable to reach consensus on: {goal}. Review positions individually."

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

    def format_debate_transcript(self, proceedings: DebateProceedings) -> str:
        """
        ISSUE 5+6 FIX: Display structured debate as auditable transcript.
        
        Shows:
        - Each minister's stance + unique doctrine count (no narrative)
        - Structured conflict events with type + severity
        - Tribunal verdict with decision + constraints
        - Truth violations if present
        
        Output is fully traceable, no invented strategy.
        """
        lines = []
        lines.append("[DARBAR PROCEEDINGS - AUDITABLE TRANSCRIPT]")
        lines.append("")
        
        # Show each turn with unique doctrine counts and violations
        for turn in proceedings.turns:
            lines.append(f"[{turn.minister.upper()}]")
            lines.append(f"  Stance: {turn.stance}")
            lines.append(f"  Justification: {turn.justification[:100]}..." if len(turn.justification) > 100 else f"  Justification: {turn.justification}")
            lines.append(f"  Unique Doctrines: {turn.unique_doctrines}")
            
            if turn.confidence:
                lines.append(f"  Confidence: {turn.confidence:.0%}")
            
            if turn.violations:
                lines.append(f"  Violations: {'; '.join(turn.violations)}")
            
            if turn.constraints:
                lines.append(f"  Constraints: {'; '.join(turn.constraints)}")
            
            if turn.risks:
                lines.append(f"  Risks: {'; '.join(turn.risks)}")
            
            lines.append("")
        
        # Show structured conflicts (ISSUE 6)
        if proceedings.conflicts:
            lines.append("[CONFLICT ANALYSIS]")
            for conflict in proceedings.conflicts:
                lines.append(f"  Type: {conflict.conflict_type}")
                lines.append(f"  Severity: {conflict.severity}")
                lines.append(f"  Parties: {', '.join(conflict.parties)}")
                lines.append(f"  Reason: {conflict.reason}")
                lines.append("")
        
        # Show hard-veto
        if proceedings.hard_veto:
            lines.append("[HARD VETO ACTIVATED]")
            lines.append("  Risk/Truth/Optionality blocked action.")
            lines.append("")
        
        # Show tribunal verdict (ISSUE 5)
        if proceedings.tribunal_verdict:
            lines.append("[TRIBUNAL VERDICT]")
            lines.append(f"  Decision: {proceedings.tribunal_verdict.decision}")
            
            if proceedings.tribunal_verdict.constraints:
                lines.append(f"  Constraints: {'; '.join(proceedings.tribunal_verdict.constraints)}")
            
            if proceedings.tribunal_verdict.required_data:
                lines.append(f"  Required Data: {'; '.join(proceedings.tribunal_verdict.required_data)}")
            
            lines.append(f"  Reasoning: {proceedings.tribunal_verdict.reasoning}")
            lines.append("")
        
        # Show final verdict
        if proceedings.final_verdict:
            lines.append("[FINAL VERDICT FROM N]")
            lines.append(f"  {proceedings.final_verdict}")
            lines.append("")
        
        return "\n".join(lines)
