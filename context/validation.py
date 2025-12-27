"""
Validation Gate - Context Risk Assessment (LOCKED)

Detects:
- High-risk patterns (existential + irreversible)
- Bias-risk patterns (high emotion + time pressure)
- Insufficient context

Feeds validation result into N's posture adjustment.
"""

from context.context_schema import DecisionContext, ValidationResult, Stakes, EmotionalLoad


class ContextValidator:
    """
    Validates extracted context against risk patterns.
    
    Does NOT approve/reject decisions.
    Only flags context for N to adjust its analysis posture.
    """
    
    def validate(self, ctx: DecisionContext) -> ValidationResult:
        """
        Validate context and return risk classification.
        
        Args:
            ctx: Decision context to validate
            
        Returns:
            ValidationResult enum
        """
        # High risk: existential stakes + irreversible consequences
        if self._is_high_risk(ctx):
            return ValidationResult.HIGH_RISK
        
        # Bias risk: high emotional load + time pressure
        if self._is_bias_risk(ctx):
            return ValidationResult.BIAS_RISK
        
        # Insufficient: not enough data collected
        if not ctx.is_validated():
            return ValidationResult.INSUFFICIENT_DATA
        
        return ValidationResult.CLEAR
    
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
