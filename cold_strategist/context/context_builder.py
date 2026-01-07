"""
Context Builder - Raw Input → Structured Context (LOCKED)

LLM-assisted, state-governed context extraction.
Short. Deterministic. Code-first.
No philosophy. No ministers yet.
"""

from typing import Optional, Dict, Any, List
from cold_strategist.context.context_schema import DecisionContext, Stakes, EmotionalLoad, ValidationResult
from cold_strategist.context.question_engine import QuestionEngine
from cold_strategist.core.gatekeeper import Gatekeeper
import uuid


class ContextBuilder:
    """
    Converts raw human input → structured decision context.
    
    Detects:
    - Domain and sub-domains
    - Stakes and irreversibility
    - Emotional load and fatigue
    - Time pressure and urgency
    - Prior patterns
    
    Stops when confidence ≥ 0.75.
    Hands clean context to N.
    """
    
    CONFIDENCE_THRESHOLD = 0.75
    
    def __init__(self, question_engine: Optional[QuestionEngine] = None):
        """
        Initialize context builder.
        
        Args:
            question_engine: QuestionEngine instance (or create default)
        """
        self.qe = question_engine or QuestionEngine()
    
    def create_context(self, raw_input: str) -> DecisionContext:
        """
        Initialize context from raw human input.
        
        Args:
            raw_input: Raw decision question/situation
            
        Returns:
            Initial DecisionContext object
        """
        ctx = DecisionContext(raw_input=raw_input)
        return ctx
    
    def needs_more_input(self, ctx: DecisionContext) -> bool:
        """
        Check if context requires more information.
        
        Args:
            ctx: Current decision context
            
        Returns:
            True if confidence < threshold
        """
        return ctx.confidence < self.CONFIDENCE_THRESHOLD
    
    def next_question(self, ctx: DecisionContext) -> Optional[str]:
        """
        Get the next necessary question.
        
        Args:
            ctx: Current decision context
            
        Returns:
            Next question string, or None if context complete
        """
        return self.qe.generate(ctx)

    def propose_question(self, ctx: DecisionContext, decision_id: Optional[str] = None, active_required_fields: Optional[Dict[str, List[str]]] = None, active_ministers: Optional[List[str]] = None, context_state: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Propose the next question but enforce Gatekeeper rules.

        If `decision_id` is None, behaves like `next_question`.
        """
        question = self.qe.generate(ctx)
        if not question:
            return None

        # If no decision_id provided, return question directly
        if decision_id is None:
            return question

        # Build minimal context_state if not provided
        if context_state is None:
            context_state = self._build_minimal_context_state(ctx)

        # Map question to a canonical field path
        field = self._map_question_to_field(question)
        if field is None:
            return "INSUFFICIENT CONTEXT — NO FURTHER PROGRESS POSSIBLE"

        # Determine requester: prefer first active minister that requires this field
        requester = None
        if active_required_fields:
            for m, reqs in active_required_fields.items():
                if field in reqs and (not active_ministers or m in active_ministers):
                    requester = m
                    break

        if requester is None:
            requester = "ContextBuilder"

        g = Gatekeeper(decision_id)
        request = {
            "requester": requester,
            "requested_field": field,
            "reason": question,
            "decision_id": decision_id,
            "context_snapshot": context_state,
        }

        verdict = g.can_ask(request, context_state, active_required_fields or {}, active_ministers or [])
        if verdict.get("status") == "ALLOWED":
            return question
        else:
            # Record rejection and terminate per rules
            g.record_rejection(request, verdict.get("reason", "REJECTED"))
            return "INSUFFICIENT CONTEXT — NO FURTHER PROGRESS POSSIBLE"

    def _map_question_to_field(self, question: str) -> Optional[str]:
        q = question.lower()
        if "what kind of situation" in q:
            return "identity.domain"
        if "worst realistic outcome" in q or "how bad" in q:
            return "risk_profile.hard_loss_cap_percent"
        if "can this be undone" in q or "lasting damage" in q:
            return "constraints.irreversibility"
        if "what emotion is strongest" in q:
            return "meta.emotional_state"
        if "faced something structurally similar" in q:
            return "meta.prior_patterns"
        return None

    def _build_minimal_context_state(self, ctx: DecisionContext) -> Dict[str, Any]:
        # Build a minimal canonical context dict as required by Gatekeeper
        return {
            "identity": {},
            "objectives": {},
            "constraints": {},
            "risk_profile": {},
            "time_horizon": {},
            "resources": {},
            "environment": {},
            "forbidden_moves": {},
            "confidence_map": {"overall_context_confidence": ctx.confidence, "unstable_fields": []},
            "meta": {}
        }
    
    def update_context(
        self, 
        ctx: DecisionContext, 
        question: str, 
        answer: str
    ) -> DecisionContext:
        """
        Update context based on human response.
        
        Args:
            ctx: Current decision context
            question: The question that was asked
            answer: Human's response
            
        Returns:
            Updated DecisionContext
        """
        answer_lower = answer.lower().strip()
        
        # Domain classification
        if "domain" in question.lower() or "kind of situation" in question.lower():
            ctx.domain = self._parse_domain(answer)
        
        # Stakes assessment
        elif "worst realistic outcome" in question.lower():
            ctx.stakes = self._parse_stakes(answer)
        
        # Irreversibility check
        elif "undo" in question.lower() or "lasting damage" in question.lower():
            ctx.irreversibility = "no" not in answer_lower
        
        # Emotional load
        elif "emotion" in question.lower() or "strongest right now" in question.lower():
            ctx.emotional_load = self._parse_emotion(answer)
        
        # Prior patterns
        elif "faced something" in question.lower() or "similar before" in question.lower():
            if "never" not in answer_lower:
                ctx.prior_patterns.append(answer)
        
        # Update confidence
        self._update_confidence(ctx)
        
        # Run validation
        ctx.validation_result = self._validate(ctx)
        
        return ctx
    
    def _parse_domain(self, answer: str) -> str:
        """Extract domain from answer."""
        answer_lower = answer.lower()
        
        domains = {
            "relationship": ["relationship", "partner", "spouse", "friend", "family"],
            "career": ["career", "job", "work", "boss", "employment", "business"],
            "conflict": ["conflict", "fight", "dispute", "argument", "enemy"],
            "money": ["money", "finance", "debt", "investment", "spending", "salary"],
            "identity": ["identity", "belief", "values", "direction", "purpose"],
        }
        
        for domain, keywords in domains.items():
            if any(kw in answer_lower for kw in keywords):
                return domain
        
        return "other"
    
    def _parse_stakes(self, answer: str) -> Stakes:
        """Infer stakes from description of worst outcome."""
        answer_lower = answer.lower()
        
        existential_keywords = [
            "death", "life", "irreversible", "survive", "extinction",
            "lose everything", "total loss", "end", "cease"
        ]
        high_keywords = [
            "serious", "major", "significant", "years", "permanent",
            "lose", "damage", "broken", "lost"
        ]
        
        if any(kw in answer_lower for kw in existential_keywords):
            return Stakes.EXISTENTIAL
        elif any(kw in answer_lower for kw in high_keywords):
            return Stakes.HIGH
        elif len(answer) > 50:  # Detailed worry = medium stakes
            return Stakes.MEDIUM
        else:
            return Stakes.LOW
    
    def _parse_emotion(self, answer: str) -> EmotionalLoad:
        """Infer emotional load from response."""
        answer_lower = answer.lower()
        
        high_emotions = ["fear", "terror", "panic", "desperate", "furious", "shame"]
        medium_emotions = ["worried", "concerned", "frustrated", "sad"]
        
        if any(e in answer_lower for e in high_emotions):
            return EmotionalLoad.HIGH
        elif any(e in answer_lower for e in medium_emotions):
            return EmotionalLoad.MEDIUM
        else:
            return EmotionalLoad.LOW
    
    def _update_confidence(self, ctx: DecisionContext) -> None:
        """
        Calculate confidence score based on filled fields.
        
        Confidence ≥ 0.75 → Context ready for validation
        
        Args:
            ctx: Decision context to update (modified in place)
        """
        fields_filled = sum([
            ctx.domain is not None,
            ctx.stakes is not None,
            ctx.irreversibility is not None,
            ctx.emotional_load is not None,
            len(ctx.prior_patterns) > 0,
        ])
        
        total_fields = 5
        ctx.confidence = fields_filled / total_fields
    
    def _validate(self, ctx: DecisionContext) -> ValidationResult:
        """
        Gate-check the context for risk patterns.
        
        Args:
            ctx: Decision context to validate
            
        Returns:
            ValidationResult enum
        """
        # High risk: existential + irreversible
        if ctx.is_high_risk():
            return ValidationResult.HIGH_RISK
        
        # Bias risk: high emotion + time pressure
        if ctx.is_biased():
            return ValidationResult.BIAS_RISK
        
        # Insufficient data
        if not ctx.is_validated():
            return ValidationResult.INSUFFICIENT_DATA
        
        return ValidationResult.CLEAR

