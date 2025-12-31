"""
Opponent Model (SAFE, ABSTRACT)

Models a SYSTEM, not a person.

Components:
- arena: Context of competition
- incentives: What the system optimizes for
- constraints: Rules the system must follow
- reaction_speed: How fast does it respond?
- visibility: How much can we see?

Opponent is ABSTRACT:
- Could be market forces
- Could be organizational structure
- Could be fictional adversary
- Could be your own limitations

No targeting individuals. No personal attacks.
"""

from typing import Dict, List, Any


def build_opponent(arena: str, constraints: List[str]) -> Dict[str, Any]:
    """
    Build abstract opponent model.
    
    Args:
        arena: Context (career, negotiation, fiction, self, etc)
        constraints: Hard constraints (legal, reversible, reputation_safe)
        
    Returns:
        Opponent model dict
        
    Opponent is a SYSTEM with incentives, constraints, and reaction patterns.
    Not a person to harm.
    """
    
    return {
        "arena": arena,
        "incentives": [
            "status",           # Improve position
            "resources",        # Acquire resources
            "risk_avoidance",   # Avoid losses
            "stability"         # Maintain status quo
        ],
        "constraints": constraints,  # Same legal/reversible constraints apply
        "reaction_speed": "medium",  # How fast does system respond?
        "visibility": "partial",     # How much can we see?
        "escalation_trigger": None   # When does conflict escalate?
    }

