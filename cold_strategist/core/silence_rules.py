from typing import Dict, Any


def should_silence(outputs: Dict[str, Dict[str, Any]], min_avg_conf: float = 0.5) -> bool:
    """Return True if the system should produce SILENCE based on confidence rules."""
    if not outputs:
        return True
    confs = [float(o.get("confidence", 0.0)) for o in outputs.values()]
    avg = sum(confs) / len(confs)
    return avg < min_avg_conf
