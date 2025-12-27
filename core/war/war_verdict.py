"""
War Verdict (SAFE, ABSTRACT)

Formats simulation results into actionable verdict.

Output:
{
  "VERDICT": "PROCEED | CONDITIONAL | ABORT",
  "PRIMARY_MOVE": description,
  "ALTERNATIVES": [alt1, alt2],
  "RISK": damage_score,
  "OPTIONALITY": preserved|limited,
  "DO_NOT": [constraints],
  "NEXT": first step
}

Simple, clear, consequence-focused.
"""

from typing import Dict, List, Any, Optional


def build_war_verdict(evaluated: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build war verdict from evaluated moves.
    
    Args:
        evaluated: Output from evaluate_damage()
        
    Returns:
        War verdict dict
    """
    
    # Filter to safe moves
    safe_moves = [e for e in evaluated if e.get("safe", False)]
    
    # If no safe moves, abort
    if not safe_moves:
        return {
            "VERDICT": "ABORT",
            "reason": "No moves have acceptable risk profile",
            "PRIMARY_MOVE": None,
            "ALTERNATIVES": [],
            "RISK": "unacceptable",
            "OPTIONALITY": "preserved",
            "DO_NOT": [
                "Unsafe moves with damage_score >= 0.6",
                "Moves that lose optionality beyond 0.2"
            ],
            "NEXT": "Wait, reassess, build resources/reduce time pressure"
        }
    
    # Sort safe moves by damage score (lowest first)
    safe_moves_sorted = sorted(safe_moves, key=lambda x: x.get("damage_score", 1.0))
    
    best_move = safe_moves_sorted[0]
    alternatives = safe_moves_sorted[1:3]
    
    # Determine verdict
    best_damage = best_move.get("damage_score", 0.5)
    
    if best_damage < 0.3:
        verdict = "PROCEED"
    elif best_damage < 0.5:
        verdict = "CONDITIONAL"
    else:
        verdict = "ABORT"
    
    # Optionality status
    optionality_loss = best_move.get("optionality_loss", 0.1)
    optionality_status = (
        "preserved" if optionality_loss < 0.15
        else "limited" if optionality_loss < 0.25
        else "constrained"
    )
    
    return {
        "VERDICT": verdict,
        "PRIMARY_MOVE": best_move.get("description", "unknown"),
        "ALTERNATIVES": [
            alt.get("description", "unknown") for alt in alternatives
        ],
        "RISK": round(best_damage, 2),
        "OPTIONALITY": optionality_status,
        "DO_NOT": [
            "Take irreversible actions",
            "Act under time pressure without buffer",
            "Escalate beyond our ability to control",
            "Lose more than 25% optionality"
        ],
        "NEXT": _get_first_step(best_move),
        "confidence": _calculate_confidence(best_damage),
        "state_check": "Verify fatigue < 0.3 and resources > 0.4 before proceeding"
    }


def _get_first_step(best_move: Dict[str, Any]) -> str:
    """
    Determine first concrete action.
    
    Args:
        best_move: Best move from evaluation
        
    Returns:
        First step string
    """
    
    move_name = best_move.get("move", "unknown")
    
    if "delay" in move_name:
        return "Set a decision deadline. Give yourself time to observe and think."
    elif "options" in move_name:
        return "Map out 2-3 parallel paths. Invest in diversity."
    elif "signal" in move_name:
        return "Clarify your boundaries clearly and consistently."
    elif "consolidate" in move_name:
        return "Lock in current advantages. Secure what you have."
    elif "escalate" in move_name:
        return "Increase cost of inaction. Make the status quo unsustainable."
    elif "cooperation" in move_name:
        return "Propose specific win-win arrangement. Make it easy to say yes."
    else:
        return "Execute first move cautiously, monitoring for unexpected reactions."


def _calculate_confidence(damage_score: float) -> float:
    """
    Calculate confidence level based on damage.
    
    Args:
        damage_score: Risk score 0-1
        
    Returns:
        Confidence 0-1 (inverse of risk)
    """
    
    return max(0.0, 1.0 - damage_score)

