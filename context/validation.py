"""
Validation Gate - Context Risk Assessment (LOCKED)

Detects:
- High-risk patterns (existential + irreversible)
- Bias-risk patterns (high emotion + time pressure)
- Insufficient context

Feeds validation result into N's posture adjustment.
"""

from dataclasses import dataclass
from typing import List

from context.context_schema import DecisionContext, ValidationResult, Stakes, EmotionalLoad

@dataclass
class ValidationOutcome:
    ok: bool
    missing_fields: List[str]
    contradictions: List[str]
    reason: str


class ContextValidator:
    """
    Validates extracted context against risk patterns.
    
    Does NOT approve/reject decisions.
    Only flags context for N to adjust its analysis posture.
    """
    
    def validate(self, ctx: DecisionContext) -> ValidationResult:
        """Compatibility wrapper that returns the legacy enum.

        New code should call `validate_structured` to get detailed
        validation outcome including missing fields and contradictions.
        """
        outcome = self.validate_structured(ctx)
        if outcome.contradictions:
            return ValidationResult.BIAS_RISK
        if outcome.missing_fields:
            return ValidationResult.INSUFFICIENT_DATA
        return ValidationResult.CLEAR

    def validate_structured(self, ctx: DecisionContext) -> ValidationOutcome:
        """Return a structured validation outcome.

        Checks for missing required fields and simple contradictions.
        """
        missing = []
        contradictions = []

        # Required fields for minimal context
        required = [
            ("domain", ctx.domain),
            ("stakes", ctx.stakes),
            ("irreversibility", ctx.irreversibility),
            ("emotional_load", ctx.emotional_load),
            ("prior_patterns", ctx.prior_patterns),
        ]

        for name, val in required:
            if not val:
                missing.append(name)

        # Simple contradiction check: low stakes but existential prior patterns
        if ctx.stakes != Stakes.EXISTENTIAL and any("death" in (p or "").lower() for p in ctx.prior_patterns):
            contradictions.append("prior_patterns_imply_higher_stakes")

        reason = "ok" if not missing and not contradictions else "issues_found"
        ok = not missing and not contradictions

        return ValidationOutcome(ok=ok, missing_fields=missing, contradictions=contradictions, reason=reason)
    
    def _is_high_risk(self, ctx: DecisionContext) -> bool:
        """
        Check for existential + irreversible pattern.
        
        Args:
            ctx: Decision context
            
        Returns:
            True if high-risk pattern detected
        """
        return (
            ctx.stakes == Stakes.EXISTENTIAL
            and ctx.irreversibility is True
        )
    
    def _is_bias_risk(self, ctx: DecisionContext) -> bool:
        """
        Check for high emotion + time pressure pattern.
        
        Args:
            ctx: Decision context
            
        Returns:
            True if bias-risk pattern detected
        """
        return (
            ctx.emotional_load == EmotionalLoad.HIGH
            and ctx.time_pressure is True
        )
    
    def risk_posture_adjustment(self, validation_result: ValidationResult) -> dict:
        """
        Return posture adjustments for N based on validation result.
        
        Args:
            validation_result: Result of context validation
            
        Returns:
            Dict of posture adjustments
        """
        adjustments = {
            ValidationResult.CLEAR: {
                "urgency": "normal",
                "scrutiny_level": "standard",
                "override_sensitivity": "low"
            },
            ValidationResult.HIGH_RISK: {
                "urgency": "critical",
                "scrutiny_level": "maximum",
                "override_sensitivity": "high",
                "require_irreversibility_analysis": True,
                "require_consequence_mapping": True
            },
            ValidationResult.BIAS_RISK: {
                "urgency": "elevated",
                "scrutiny_level": "high",
                "override_sensitivity": "medium",
                "bias_warning": "High emotion detected. Elevate rationality checks.",
                "require_cooling_period_option": True
            },
            ValidationResult.INSUFFICIENT_DATA: {
                "urgency": "defer",
                "scrutiny_level": "standard",
                "action": "return to context building"
            }
        }
        
        return adjustments.get(validation_result, {})
