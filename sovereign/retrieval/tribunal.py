from ..config.thresholds import DISAGREEMENT_THRESHOLD

def tribunal_required(council_outputs: dict) -> bool:
    """Check if Tribunal needed (high disagreement)."""
    confidences = [v["confidence"] for v in council_outputs.values()]
    if not confidences:
        return False
    return max(confidences) - min(confidences) > DISAGREEMENT_THRESHOLD

def tribunal_verdict(council_outputs: dict) -> str:
    """Issue Tribunal verdict: ALLOW, SILENCE, or ESCALATE."""
    if not council_outputs:
        return "SILENCE"
    
    confidences = [v["confidence"] for v in council_outputs.values()]
    avg = sum(confidences) / len(confidences)
    
    if avg < 0.3:
        return "ESCALATE"
    elif avg < 0.4:
        return "SILENCE"
    else:
        return "ALLOW"
