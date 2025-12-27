"""
War Mode Engine - Knowledge-grounded asymmetric advice with safe constraints.

War Mode enhances Normal Mode by:
1. Suppressing soft biases (moral veto, comfort bias, reputational risk)
2. Relaxing counter-evidence filters (show more "warning" patterns)
3. Increasing minister selection asymmetry (favor aggressive ministers)
4. Enforcing hard constraints (legality, individual harm, truthfulness)
5. Logging all suppressions and decisions
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from core.war.war_policy import WarModePolicy, WarModeFilter, DEFAULT_WAR_POLICY
from core.war.war_logger import WarModeLogger
from core.knowledge.minister_retriever import MinisterRetriever
from core.knowledge.synthesize.minister_synthesizer import MinisterSynthesizer
from core.knowledge.war_aware_rag_retriever import WarAwareRAGRetriever
from darbar.tribunal import Tribunal
from darbar.n import N


@dataclass
class WarModeAdvice:
    """Single piece of advice with War Mode filtering applied."""
    minister: str
    status: str  # "APPROVED", "SUPPRESSED_SOFT", "REJECTED_HARD"
    advice: Optional[str]
    rationale: Optional[str]
    confidence: float
    violations: List[str]
    suppressed_filters: List[str]
    citations: List[Dict[str, str]]


@dataclass
class WarModeVerdict:
    """Complete War Mode analysis with full audit trail."""
    goal: str
    approved_advice: List[WarModeAdvice]
    suppressed_soft_advice: List[WarModeAdvice]
    rejected_hard_advice: List[WarModeAdvice]
    risk_assessment: Dict[str, Any]
    audit_trail: str
    final_recommendation: str
    event_id: Optional[str]


class WarEngine:
    """
    Execute War Mode analysis with knowledge-grounded, safe constraints.
    """
    
    def __init__(
        self,
        retriever: MinisterRetriever,
        synthesizer: MinisterSynthesizer,
        policy: Optional[WarModePolicy] = None,
    ):
        """
        Args:
            retriever: MinisterRetriever instance
            synthesizer: MinisterSynthesizer instance
            policy: WarModePolicy (uses default if None)
        """
        self.retriever = retriever
        self.synthesizer = synthesizer
        self.policy = policy or DEFAULT_WAR_POLICY
        self.filter = WarModeFilter(self.policy)
        self.logger = WarModeLogger()
        self.tribunal = Tribunal()
        self.n = N()
    
    def run(
        self,
        goal: str,
        context: Dict[str, Any],
        state: Dict[str, Any],
        arena: str = "default",
        constraints: Optional[Dict[str, bool]] = None,
        log_to_memory: bool = True,
    ) -> WarModeVerdict:
        """
        Execute War Mode analysis.
        
        Args:
            goal: User's objective
            context: Current situation context
            state: Current state (fatigue, resources, etc.)
            arena: Arena/domain for analysis
            constraints: Override default constraints (suppress/enforce)
            log_to_memory: Whether to log to memory store
        
        Returns:
            WarModeVerdict with all advice, suppressions, and audit trail
        """
        # Start logging session
        constraints = constraints or {}
        self.logger.start_session(goal, constraints)
        
        # Select ministers (bias toward aggressive in War Mode)
        ministers = self._select_war_ministers()
        
        all_advice = {
            "approved": [],
            "suppressed_soft": [],
            "rejected_hard": [],
        }
        
        # Get advice from each minister
        for minister in ministers:
            advice_item = self._get_filtered_advice(
                minister=minister,
                goal=goal,
                context=context,
            )
            
            # Log evaluation
            self.logger.log_advice_evaluation(
                minister=minister,
                query=goal,
                status=advice_item.status,
                advice=advice_item.advice or "",
                violations=advice_item.violations,
                suppressed_filters=advice_item.suppressed_filters,
                confidence=advice_item.confidence,
                citations=advice_item.citations,
            )
            
            # Categorize
            if advice_item.status == "APPROVED":
                all_advice["approved"].append(advice_item)
            elif advice_item.status == "SUPPRESSED_SOFT":
                all_advice["suppressed_soft"].append(advice_item)
            else:
                all_advice["rejected_hard"].append(advice_item)
        
        # Risk assessment
        risk_assessment = self._assess_risk(all_advice, context, state)
        self.logger.log_risk_assessment(
            risk_level=risk_assessment.get("level"),
            description=risk_assessment.get("description"),
            mitigations=risk_assessment.get("mitigations", []),
        )
        
        # Frame final recommendation
        final_verdict = self._frame_war_verdict(all_advice, risk_assessment, goal)
        
        # End logging
        audit_trail = self.logger.get_audit_trail()
        
        return WarModeVerdict(
            goal=goal,
            approved_advice=all_advice["approved"],
            suppressed_soft_advice=all_advice["suppressed_soft"],
            rejected_hard_advice=all_advice["rejected_hard"],
            risk_assessment=risk_assessment,
            audit_trail=audit_trail,
            final_recommendation=final_verdict,
            event_id=None,  # To be filled by caller
        )
    
    def _select_war_ministers(self) -> List[str]:
        """
        Select ministers for War Mode (bias toward aggressive).
        
        In War Mode, favor ministers with strong asymmetric views:
        - power, conflict, strategy (aggressive)
        - diplomacy, psychology (manipulation-aware)
        - truth (grounding in reality)
        """
        return [
            "power",
            "conflict",
            "strategy",
            "diplomacy",
            "psychology",
            "truth",
        ]
    
    def _get_filtered_advice(
        self,
        minister: str,
        goal: str,
        context: Dict[str, Any],
    ) -> WarModeAdvice:
        """
        Retrieve knowledge, synthesize advice, and apply War Mode filters.
        """
        try:
            # Retrieve knowledge (include counter-evidence in War Mode)
            try:
                war_retriever = WarAwareRAGRetriever(base_retriever=self.retriever)
                retrieved = war_retriever.retrieve_for_minister(
                    minister_name=minister,
                    query=goal,
                    mode="war",
                    k=5,
                    include_counter=True,
                    include_audit=False,
                )
            except Exception:
                # Fallback to base retriever on error
                retrieved = self.retriever.retrieve_for_minister(
                    minister_name=minister,
                    query=goal,
                    k=5,
                    include_counter=True,
                )
            
            # Synthesize advice
            synthesis = self.synthesizer.synthesize(
                minister_name=minister,
                goal=goal,
                context=context,
                retrieved=retrieved,
                confidence_threshold=0.5,  # Lower threshold in War Mode
            )
            
            # Evaluate constraints
            constraints = {
                "legality": self._check_legality(synthesis.get("advice", "")),
                "individual_harm": self._check_individual_harm(synthesis.get("advice", "")),
                "truthfulness": self._check_truthfulness(synthesis.get("citations", [])),
                "moral_veto": self._check_moral_veto(synthesis.get("advice", "")),
                "comfort_bias": self._check_comfort_bias(synthesis.get("advice", "")),
                "reputational_risk": self._check_reputational_risk(synthesis.get("advice", "")),
            }
            
            # Apply filters
            filtered = self.filter.filter_advice(
                advice=synthesis.get("advice"),
                rationale=synthesis.get("rationale"),
                citations=synthesis.get("citations", []),
                constraints=constraints,
            )
            
            return WarModeAdvice(
                minister=minister,
                status=filtered["status"],
                advice=filtered["advice"],
                rationale=filtered["rationale"],
                confidence=synthesis.get("confidence", 0.0),
                violations=filtered["violations"],
                suppressed_filters=filtered["suppressed_filters"],
                citations=filtered["citations"],
            )
        
        except Exception as e:
            self.logger.log_rejected_advice(
                minister=minister,
                reason=f"Error: {str(e)}",
                soft_reason=False,
            )
            return WarModeAdvice(
                minister=minister,
                status="REJECTED_HARD",
                advice=None,
                rationale=f"Error: {str(e)}",
                confidence=0.0,
                violations=["unknown"],
                suppressed_filters=[],
                citations=[],
            )
    
    # Constraint checkers (placeholder - would use semantic analysis in production)
    def _check_legality(self, advice: str) -> bool:
        """Check if advice violates known laws."""
        illegal_keywords = ["kill", "steal", "fraud", "abuse"]
        return any(kw in advice.lower() for kw in illegal_keywords)
    
    def _check_individual_harm(self, advice: str) -> bool:
        """Check if advice targets specific individuals for harm."""
        return "target" in advice.lower() and "harm" in advice.lower()
    
    def _check_truthfulness(self, citations: List[Dict[str, str]]) -> bool:
        """Check if advice is grounded in retrieved knowledge."""
        return len(citations) > 0  # Must have sources
    
    def _check_moral_veto(self, advice: str) -> bool:
        """Check if advice would fail a moral check."""
        moral_keywords = ["unethical", "immoral", "wrong"]
        return any(kw in advice.lower() for kw in moral_keywords)
    
    def _check_comfort_bias(self, advice: str) -> bool:
        """Check if advice is uncomfortably direct."""
        return len(advice) > 0  # All advice checked (subjective)
    
    def _check_reputational_risk(self, advice: str) -> bool:
        """Check if advice carries reputational risk."""
        risky_keywords = ["controversial", "risky", "damaging"]
        return any(kw in advice.lower() for kw in risky_keywords)
    
    def _assess_risk(
        self,
        all_advice: Dict[str, List[WarModeAdvice]],
        context: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess overall risk of War Mode advice.
        """
        suppressed_count = len(all_advice["suppressed_soft"])
        rejected_count = len(all_advice["rejected_hard"])
        approved_count = len(all_advice["approved"])
        
        if rejected_count > 2:
            risk_level = "CRITICAL"
        elif suppressed_count > 3 or approved_count == 0:
            risk_level = "HIGH"
        elif suppressed_count > 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "level": risk_level,
            "description": f"War Mode: {approved_count} approved, {suppressed_count} suppressed soft, {rejected_count} rejected hard",
            "mitigations": [
                "Monitor implementation closely",
                "Be prepared to escalate or withdraw",
                "Document all decisions and outcomes",
                "Review suppressed advice after action completes",
            ],
        }
    
    def _frame_war_verdict(
        self,
        all_advice: Dict[str, List[WarModeAdvice]],
        risk_assessment: Dict[str, Any],
        goal: str,
    ) -> str:
        """
        Frame final War Mode verdict.
        """
        lines = [
            "=" * 60,
            "WAR MODE VERDICT (Force Posture)",
            "=" * 60,
            "",
            f"GOAL: {goal}",
            f"RISK LEVEL: {risk_assessment['level']}",
            "",
        ]
        
        approved = all_advice["approved"]
        if approved:
            lines.append("APPROVED ADVICE (passed all constraints):")
            for advice in approved:
                lines.append(f"  {advice.minister.upper()}: {advice.advice or '[no text]'}")
            lines.append("")
        
        suppressed = all_advice["suppressed_soft"]
        if suppressed:
            lines.append(f"SUPPRESSED SOFT CONSTRAINTS ({len(suppressed)} items):")
            for advice in suppressed:
                filters = ", ".join(advice.suppressed_filters)
                lines.append(f"  {advice.minister.upper()}: suppressed [{filters}]")
            lines.append("")
        
        rejected = all_advice["rejected_hard"]
        if rejected:
            lines.append(f"REJECTED HARD CONSTRAINTS ({len(rejected)} items):")
            for advice in rejected:
                lines.append(f"  {advice.minister.upper()}: {', '.join(advice.violations)}")
            lines.append("")
        
        lines.append("MITIGATIONS:")
        for mit in risk_assessment.get("mitigations", []):
            lines.append(f"  - {mit}")
        
        return "\n".join(lines)
    - N's bluntness adjusts based on war history
    """
    
    def run(
        self,
        objective: str,
        arena: str,
        constraints: List[str],
        state: Optional[Dict] = None,
        log_to_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete war mode analysis.
        
        Args:
            objective: What you're trying to achieve
            arena: Context (career, negotiation, fiction, self, etc)
            constraints: Hard constraints (legal, reversible, reputation_safe)
            state: Current state (fatigue, resources, etc)
            log_to_memory: If True, log this analysis to memory
            
        Returns:
            War verdict dict with PRIMARY_MOVE, ALTERNATIVES, RISK, etc.
            If log_to_memory=True, includes EVENT_ID for outcome resolution
        """
        
        if state is None:
            state = {}
        
        # Phase 1: Model the system/opponent
        opponent = build_opponent(arena, constraints)
        
        # Phase 2: Generate legal/reversible moves
        moves = generate_moves(objective, constraints)
        
        # Phase 3: Simulate responses
        simulations = simulate_counters(moves, opponent)
        
        # Phase 4: Evaluate damage/risk
        evaluated = evaluate_damage(simulations, state)
        
        # Phase 5: Build verdict
        verdict = build_war_verdict(evaluated)
        
        # Phase 6: Log to memory if enabled
        if log_to_memory:
            ministers = [
                "Power",       # Resource control
                "Timing",      # When to act
                "Optionality", # Exit routes
                "Risk",        # Damage envelope
                "Truth",       # Reality check
                "N"            # Synthesis layer
            ]
            
            event_id = log_war_event(
                objective=objective,
                arena=arena,
                verdict=verdict,
                state=state,
                ministers=ministers
            )
            
            verdict["EVENT_ID"] = event_id
        
        return verdict
