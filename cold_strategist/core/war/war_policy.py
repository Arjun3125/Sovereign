"""
War Mode Policy - Defines posture shift and constraint enforcement.

War Mode suppresses BIASES (soft filters), not LAWS (hard constraints).

Safe constraints that are NEVER suppressed:
- Legality: All advice must obey applicable law
- Individual harm: No targeting specific individuals for harm
- Truthfulness: All claims must be grounded in retrieved knowledge

Suppressible biases:
- Moral veto: Don't block advice for being "unethical" per se
- Comfort bias: Don't soften uncomfortable truths
- Reputational risk: Acknowledge but don't avoid action due to reputation
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class WarModePolicy:
    """
    Configuration for War Mode posture shift.
    """
    
    # Hard constraints (NEVER suppressed)
    legality_enforced: bool = True
    no_individual_targeting: bool = True
    truthfulness_required: bool = True
    
    # Suppressible biases
    moral_veto_suppressed: bool = True
    comfort_bias_suppressed: bool = True
    reputational_risk_suppressed: bool = True
    
    # Logging
    log_suppressions: bool = True
    log_rejected_advice: bool = True
    log_risk_assessment: bool = True


# Default War Mode policy
DEFAULT_WAR_POLICY = WarModePolicy(
    legality_enforced=True,
    no_individual_targeting=True,
    truthfulness_required=True,
    moral_veto_suppressed=True,
    comfort_bias_suppressed=True,
    reputational_risk_suppressed=True,
    log_suppressions=True,
    log_rejected_advice=True,
    log_risk_assessment=True,
)


def evaluate_constraint(constraint_name: str, value: bool, policy: WarModePolicy) -> bool:
    """
    Check if constraint is enforced under given policy.
    
    Hard constraints always return True (enforced).
    Soft constraints may be suppressed by policy.
    
    Args:
        constraint_name: "legality" | "individual_harm" | "truthfulness" |
                        "moral_veto" | "comfort_bias" | "reputational_risk"
        value: Current constraint state
        policy: WarModePolicy instance
    
    Returns:
        True if constraint is enforced, False if suppressed
    """
    # Hard constraints (always enforced)
    if constraint_name == "legality":
        return policy.legality_enforced
    elif constraint_name == "individual_harm":
        return policy.no_individual_targeting
    elif constraint_name == "truthfulness":
        return policy.truthfulness_required
    
    # Soft constraints (may be suppressed)
    elif constraint_name == "moral_veto":
        return not policy.moral_veto_suppressed
    elif constraint_name == "comfort_bias":
        return not policy.comfort_bias_suppressed
    elif constraint_name == "reputational_risk":
        return not policy.reputational_risk_suppressed
    
    else:
        raise ValueError(f"Unknown constraint: {constraint_name}")


class WarModeFilter:
    """
    Applies War Mode policy to advice before returning to user.
    
    - Rejects advice that violates hard constraints
    - Flags but allows advice that violates soft constraints (if suppressed)
    - Logs all filtering decisions for audit trail
    """
    
    def __init__(self, policy: WarModePolicy = None):
        self.policy = policy or DEFAULT_WAR_POLICY
        self.filtered_items = []  # For audit trail
    
    def filter_advice(
        self,
        advice: str,
        rationale: str,
        citations: list,
        constraints: Dict[str, bool],
    ) -> Dict[str, Any]:
        """
        Apply War Mode filtering to advice.
        
        Args:
            advice: Minister's advice text
            rationale: Explanation
            citations: Source references
            constraints: Dict of constraint names → violated (True = constraint violated)
        
        Returns:
            {
              "status": "APPROVED" | "SUPPRESSED_SOFT" | "REJECTED_HARD",
              "advice": advice,
              "rationale": rationale,
              "violations": [list of violated constraints],
              "suppressed_filters": [list of filters that were suppressed],
              "citations": citations,
            }
        """
        violations = {k: v for k, v in constraints.items() if v}
        rejected_hard = []
        suppressed_soft = []
        
        # Check hard constraints
        hard_constraints = ["legality", "individual_harm", "truthfulness"]
        for constraint in hard_constraints:
            if constraint in violations and violations[constraint]:
                rejected_hard.append(constraint)
        
        if rejected_hard:
            return {
                "status": "REJECTED_HARD",
                "advice": None,
                "rationale": f"Violates hard constraints: {', '.join(rejected_hard)}",
                "violations": rejected_hard,
                "suppressed_filters": [],
                "citations": [],
            }
        
        # Check soft constraints
        soft_constraints = ["moral_veto", "comfort_bias", "reputational_risk"]
        for constraint in soft_constraints:
            if constraint in violations and violations[constraint]:
                is_suppressed = not evaluate_constraint(constraint, True, self.policy)
                if is_suppressed:
                    suppressed_soft.append(constraint)
                else:
                    # Soft constraint violated and NOT suppressed → reject
                    rejected_hard.append(constraint)
        
        if suppressed_soft:
            status = "SUPPRESSED_SOFT"
        else:
            status = "APPROVED"
        
        result = {
            "status": status,
            "advice": advice,
            "rationale": rationale,
            "violations": [k for k, v in violations.items() if v],
            "suppressed_filters": suppressed_soft,
            "citations": citations,
        }
        
        self.filtered_items.append(result)
        return result
