"""
Damage Envelope (SAFE, ABSTRACT)

Evaluates risk bounds for each move.

For each simulated move:
- What's the damage score (0-1)?
- Is it safe (damage < 0.6)?
- What state factors increase risk?

State factors:
- fatigue: 0-1 (how tired are you?)
- resources: 0-1 (how much do you have?)
- time_pressure: 0-1 (how urgent?)
"""

from typing import Dict, List, Any


def evaluate_damage(simulations: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluate risk and safety of each move.
    
    Args:
        simulations: Simulated moves from simulate_counters()
        state: Current state (fatigue, resources, time_pressure)
        
    Returns:
        Evaluated simulations with damage scores
    """
    
    # Extract state factors
    fatigue = state.get("fatigue", 0.0)
    resources = state.get("resources", 0.5)
    time_pressure = state.get("time_pressure", 0.0)
    
    evaluated = []
    
    for s in simulations:
        # Base damage from move
        escalation_risk = s.get("escalation_risk", 0.2)
        optionality_loss = s.get("optionality_loss", 0.1)
        
        # State factors increase risk
        fatigue_multiplier = 1.0 + fatigue
        time_pressure_multiplier = 1.0 + time_pressure
        
        # Resource scarcity makes moves riskier
        resource_factor = (1.0 - resources) * 0.2
        
        # Total damage
        total_damage = (
            escalation_risk +
            (optionality_loss * 0.5) +
            (fatigue * 0.1) +
            (time_pressure * 0.15) +
            resource_factor
        )
        
        # Cap at 1.0
        damage_score = min(total_damage, 1.0)
        
        # Safety threshold
        is_safe = damage_score < 0.6
        
        evaluated.append({
            **s,
            "damage_score": round(damage_score, 2),
            "safe": is_safe,
            "escalation_risk": escalation_risk,
            "optionality_loss": optionality_loss,
            "state_factors": {
                "fatigue": fatigue,
                "resources": resources,
                "time_pressure": time_pressure
            }
        })
    
    return evaluated
