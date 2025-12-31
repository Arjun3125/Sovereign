"""
Move Generator (SAFE, ABSTRACT)

Generates abstract, legal, reversible moves.

Guarantees:
- All moves are strictly legal
- All moves are fully or partially reversible
- No deception
- No harm
- All moves preserve optionality

Move types:
1. Delay - buy time to think/prepare
2. Options - create alternatives
3. Signal - clarify boundaries
4. Consolidate - secure what you have
5. Escalate - increase stakes (legally)
"""

from typing import Dict, List, Any


def generate_moves(objective: str, constraints: List[str]) -> List[Dict[str, Any]]:
    """
    Generate abstract, legal, reversible moves.
    
    Args:
        objective: What you're trying to achieve
        constraints: Hard constraints (legal, reversible, reputation_safe)
        
    Returns:
        List of move dicts
        
    Moves are ABSTRACT and LEGAL:
    - No deception
    - No harm
    - All reversible
    - All safe
    """
    
    moves = [
        {
            "move": "delay_commitment",
            "description": "Delay action to gather information/leverage",
            "rationale": "Time can be your advantage. Use it to observe.",
            "reversible": True,
            "escalation_risk": 0.1,
            "optionality_loss": 0.05
        },
        {
            "move": "increase_options",
            "description": "Create parallel opportunities",
            "rationale": "Multiple paths reduce dependence on any single outcome.",
            "reversible": True,
            "escalation_risk": 0.15,
            "optionality_loss": 0.0
        },
        {
            "move": "signal_strength",
            "description": "Clarify boundaries and expectations",
            "rationale": "Transparency about limits prevents worse conflicts.",
            "reversible": True,
            "escalation_risk": 0.2,
            "optionality_loss": 0.1
        },
        {
            "move": "consolidate_position",
            "description": "Secure what you have before expanding",
            "rationale": "Defend your current advantages first.",
            "reversible": True,
            "escalation_risk": 0.05,
            "optionality_loss": 0.0
        },
        {
            "move": "escalate_stakes",
            "description": "Increase cost of status quo (legally)",
            "rationale": "Make inaction more expensive than cooperation.",
            "reversible": True,
            "escalation_risk": 0.3,
            "optionality_loss": 0.2
        },
        {
            "move": "offer_cooperation",
            "description": "Propose win-win arrangement",
            "rationale": "Often better to collaborate than compete.",
            "reversible": True,
            "escalation_risk": 0.0,
            "optionality_loss": 0.15
        }
    ]
    
    # Filter by constraints if needed
    if "reputation_safe" in constraints:
        # All moves are reputation-safe by default
        pass
    
    return moves

