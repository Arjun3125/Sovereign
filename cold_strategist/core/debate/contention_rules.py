"""
Contention Rules - Hard Constraints on Minister Speech (LOCKED)

No consensus.
No repetition.
One warning per issue.
No ethical language.
No sugarcoating.

Violations are caught and flagged. Ministers must revise.
"""

from typing import List, Tuple
from core.debate.debate_schema import MinisterVerdict, Objection


class ContentionRules:
    """
    Enforces hard rules on what ministers can say.
    
    Rules are non-negotiable. Violations caught and returned for revision.
    """
    
    FORBIDDEN_ETHICAL_TERMS = [
        "good",
        "bad",
        "right",
        "wrong",
        "moral",
        "moral",
        "ethics",
        "ethical",
        "should",
        "deserve",
        "fair",
        "unfair",
        "just",
        "unjust",
        "honorable",
        "dishonorable",
        "virtuous",
        "vicious"
    ]
    
    def validate_verdict(self, verdict: MinisterVerdict) -> Tuple[bool, List[str]]:
        """
        Validate a minister's verdict against contention rules.
        
        Args:
            verdict: MinisterVerdict to validate
            
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # Check for ethical language
        ethical_violations = self._check_ethical_language(
            verdict.position + " " + verdict.warning
        )
        if ethical_violations:
            violations.extend(ethical_violations)
        
        # Check for sugarcoating
        if self._is_sugarcoated(verdict.warning):
            violations.append("SUGARCOATING: Warning is too soft or vague")
        
        # Check for minimum specificity
        if len(verdict.position) < 20:
            violations.append("VAGUE: Position must be concrete and specific")
        
        if len(verdict.warning) < 20:
            violations.append("VAGUE: Warning must be concrete, not abstract")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def validate_objection(
        self,
        objection: Objection,
        prior_objections: List[Objection]
    ) -> Tuple[bool, List[str]]:
        """
        Validate an objection against contention rules.
        
        Args:
            objection: Objection to validate
            prior_objections: All prior objections in this round
            
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # Check for ethical language
        ethical_violations = self._check_ethical_language(objection.statement)
        if ethical_violations:
            violations.extend(ethical_violations)
        
        # Check for repetition
        same_type_objections = [
            o for o in prior_objections
            if o.target_minister == objection.target_minister
            and o.objection_type == objection.objection_type
        ]
        if same_type_objections:
            violations.append(
                f"REPETITION: {objection.objector} already objected "
                f"to {objection.target_minister} on {objection.objection_type}"
            )
        
        # Check for minimum specificity
        if len(objection.statement) < 30:
            violations.append("VAGUE: Objection must explain why in detail")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def _check_ethical_language(self, text: str) -> List[str]:
        """
        Detect forbidden ethical/moral language.
        
        Args:
            text: Text to check
            
        Returns:
            List of violations found
        """
        violations = []
        text_lower = text.lower()
        
        for term in self.FORBIDDEN_ETHICAL_TERMS:
            if term in text_lower:
                violations.append(
                    f"ETHICS_VIOLATION: '{term}' is forbidden ethical language. "
                    "Use factual analysis instead."
                )
        
        return violations
    
    def _is_sugarcoated(self, warning: str) -> bool:
        """
        Detect vague or soft warnings (sugarcoating).
        
        Args:
            warning: Warning text
            
        Returns:
            True if warning appears sugarcoated
        """
        soft_language = [
            "might",
            "could",
            "perhaps",
            "possibly",
            "somewhat",
            "relatively",
            "fairly"
        ]
        
        warning_lower = warning.lower()
        soft_count = sum(1 for term in soft_language if term in warning_lower)
        
        # More than 2 soft qualifiers = sugarcoating
        return soft_count > 2
    
    def get_rules_summary(self) -> str:
        """Get human-readable summary of contention rules."""
        return """
HARD CONTENTION RULES (No Exceptions):

1. NO_CONSENSUS: Ministers must take positions; vague hand-waving forbidden
2. NO_REPETITION: Same objection type cannot be filed twice against same minister
3. ONE_WARNING_PER_ISSUE: Each position gets one core warning (not 10)
4. NO_ETHICAL_LANGUAGE: No 'good', 'bad', 'should', 'deserve', 'fair', etc.
5. NO_SUGARCOATING: Warnings must be direct and concrete, not soft hedges

Violations caught in validation round. Minister must revise or withdraw.
"""
