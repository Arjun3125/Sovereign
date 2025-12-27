"""
War Calibration - Adjust N's Posture Based on War Pattern History

After war events are logged, outcomes resolved, and patterns detected,
this module adjusts N's bluntness and authority based on observed results.

Patterns inform adjustments:
- war_escalation_bias: increase caution tone, reduce confidence in escalation
- war_false_urgency_loop: require higher evidence for "urgent" claims
- war_repeated_overrides: increase bluntness (sovereign ignores anyway)

Calibrations persist so future war verdicts are shaped by past outcomes.
"""

from typing import Dict, List, Optional
from core.memory.memory_store import MemoryStore
from core.memory.pattern_engine import PatternEngine, Pattern


def calibrate_n_from_war_patterns() -> Dict[str, float]:
    """
    Detect war patterns and adjust N's confidence/bluntness parameters.
    
    Returns:
        Calibration adjustments as {param_name: adjustment_factor}
        - war_caution: factor to reduce confidence in escalation
        - war_urgency_threshold: raise evidence bar for urgency claims
        - war_bluntness: increase directness if sovereign keeps overriding
    """
    
    store = MemoryStore()
    
    # Load all events
    events = store.load_events()
    
    # Detect patterns
    engine = PatternEngine()
    patterns = engine.detect_patterns(events)
    
    # Start with neutral adjustments
    adjustments = {
        "war_caution": 1.0,           # 1.0 = no change, < 1.0 = more cautious
        "war_urgency_threshold": 1.0, # 1.0 = no change, > 1.0 = higher bar for urgency
        "war_bluntness": 1.0,          # 1.0 = no change, > 1.0 = more blunt
    }
    
    # Extract war patterns
    war_patterns = [p for p in patterns if p.domain == "war"]
    
    for pattern in war_patterns:
        if pattern.pattern_name == "war_escalation_bias":
            # Escalation keeps causing damage → reduce confidence in escalation
            adjustments["war_caution"] *= 0.7  # 30% more cautious
            
        elif pattern.pattern_name == "war_false_urgency_loop":
            # High urgency claims keep failing → raise evidence bar
            adjustments["war_urgency_threshold"] *= 1.5  # 50% higher bar
            
        elif pattern.pattern_name == "war_repeated_overrides":
            # Sovereign repeatedly ignores counsel → be more direct
            adjustments["war_bluntness"] *= 1.3  # 30% more blunt
    
    # Save calibrations
    from core.memory.confidence_adjuster import MinisterCalibration
    calibrations = MinisterCalibration()
    
    # Store N's war calibrations
    for param, factor in adjustments.items():
        calibrations.set_confidence("N", "war", factor)
    
    try:
        store.save_calibrations(calibrations)
    except Exception:
        pass  # Fail silently
    
    return adjustments


def get_n_war_posture(calibrations: Optional[Dict[str, float]] = None) -> Dict[str, any]:
    """
    Get N's current war posture (confidence, bluntness, urgency threshold).
    
    Args:
        calibrations: Optional pre-computed calibrations. If None, loads from store.
        
    Returns:
        N's war posture settings
    """
    if calibrations is None:
        calibrations = calibrate_n_from_war_patterns()
    
    return {
        "domain": "war",
        "caution": calibrations.get("war_caution", 1.0),
        "urgency_threshold": calibrations.get("war_urgency_threshold", 1.0),
        "bluntness": calibrations.get("war_bluntness", 1.0),
        "description": _posture_description(calibrations)
    }


def _posture_description(calibrations: Dict[str, float]) -> str:
    """Generate human-readable description of N's adjusted war posture."""
    caution = calibrations.get("war_caution", 1.0)
    urgency = calibrations.get("war_urgency_threshold", 1.0)
    bluntness = calibrations.get("war_bluntness", 1.0)
    
    desc_parts = []
    
    if caution < 0.8:
        desc_parts.append("heightened caution on escalation")
    if urgency > 1.3:
        desc_parts.append("skepticism toward urgency claims")
    if bluntness > 1.2:
        desc_parts.append("direct/blunt counsel style")
    
    if not desc_parts:
        return "baseline war posture"
    
    return "; ".join(desc_parts)


def summarize_war_learning() -> str:
    """
    Generate summary of what N has learned from war patterns.
    
    Returns:
        Human-readable learning summary
    """
    store = MemoryStore()
    events = store.load_events()
    war_events = [e for e in events if e.domain == "war"]
    
    if not war_events:
        return "No war-mode learning yet."
    
    engine = PatternEngine()
    patterns = engine.detect_patterns(events)
    war_patterns = [p for p in patterns if p.domain == "war"]
    
    calibrations = calibrate_n_from_war_patterns()
    
    lines = [
        f"WAR LEARNING ({len(war_events)} war events):\n",
        f"• Events: {len(war_events)}",
        f"• Patterns detected: {len(war_patterns)}",
    ]
    
    if war_patterns:
        lines.append("• Pattern insights:")
        for p in war_patterns:
            lines.append(f"  - {p.pattern_name} (freq {p.frequency})")
    
    lines.append("")
    lines.append("N's Adjusted Posture:")
    posture = get_n_war_posture(calibrations)
    lines.append(f"  {posture['description']}")
    
    return "\n".join(lines)
