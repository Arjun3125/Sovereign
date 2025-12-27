"""
Counter Simulator (SAFE, ABSTRACT)

Simulates how a system responds to each move.

For each move:
- What neutral response might we get?
- What's the escalation risk?
- How much optionality do we lose?

Abstract: assumes rational, self-interested responses.
No modeling of malice or irrationality.
"""

from typing import Dict, List, Any


def simulate_counters(moves: List[Dict[str, Any]], opponent: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Simulate system responses to our moves.
    
    Args:
        moves: List of moves from generate_moves()
        opponent: Opponent model from build_opponent()
        
    Returns:
        List of simulations with response predictions
    """
    
    simulations = []
    
    for m in moves:
        simulation = {
            "move": m["move"],
            "description": m["description"],
            "opponent_response": _predict_response(m, opponent),
            "escalation_risk": m.get("escalation_risk", 0.2),
            "optionality_loss": m.get("optionality_loss", 0.1),
            "outcome_probability": _estimate_success_probability(m)
        }
        
        simulations.append(simulation)
    
    return simulations


def _predict_response(move: Dict[str, Any], opponent: Dict[str, Any]) -> str:
    """
    Predict what system will do in response.
    
    Args:
        move: Our move
        opponent: Opponent model
        
    Returns:
        Predicted response string
    """
    
    move_name = move.get("move", "unknown")
    
    # Abstract responses
    if "delay" in move_name:
        return "Accept delay, use time to prepare counter"
    elif "options" in move_name:
        return "Neutral adjustment, may create parallel options"
    elif "signal" in move_name:
        return "Acknowledge boundaries, continue with understanding"
    elif "consolidate" in move_name:
        return "Minimal response, focus on own position"
    elif "escalate" in move_name:
        return "Matching escalation or seeking negotiation"
    elif "cooperation" in move_name:
        return "Evaluate proposal, conditional acceptance possible"
    else:
        return "neutral_adjustment"


def _estimate_success_probability(move: Dict[str, Any]) -> float:
    """
    Estimate how likely the move achieves its goal.
    
    Args:
        move: Move dict
        
    Returns:
        Success probability 0-1
    """
    
    # Base: rationality assumption
    base = 0.6
    
    # Adjust by reversibility (reversible = higher success)
    if move.get("reversible", True):
        base += 0.15
    
    # Adjust by escalation risk (lower risk = higher success)
    escalation_risk = move.get("escalation_risk", 0.2)
    base -= (escalation_risk * 0.2)
    
    return max(0.0, min(1.0, base))

