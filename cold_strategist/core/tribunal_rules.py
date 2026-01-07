from typing import Any


def should_trigger_tribunal(disagreement: float, outputs: dict) -> bool:
    """
    Hard-rule tribunal trigger.
    Accepts outputs mapping minister_id -> dict with keys: content (dict), confidence (float), minister_id (str)
    """
    try:
        if disagreement >= 0.6:
            return True

        for o in outputs.values():
            # support both dict and simple objects
            content = None
            minister_id = None
            confidence = 0.0
            if isinstance(o, dict):
                content = o.get("content", {}) or {}
                minister_id = o.get("minister_id")
                confidence = float(o.get("confidence", 0.0) or 0.0)
            else:
                content = getattr(o, "content", {}) or {}
                minister_id = getattr(o, "minister_id", None)
                confidence = float(getattr(o, "confidence", 0.0) or 0.0)

            if isinstance(content, dict) and content.get("catastrophic_risk") is True:
                return True

            if minister_id == "risk" and confidence >= 0.7:
                return True

        # Zero confident ministers
        if all((float(o.get("confidence", 0.0) if isinstance(o, dict) else getattr(o, "confidence", 0.0)) < 0.6) for o in outputs.values()):
            return True

    except Exception:
        # On error, be conservative and trigger tribunal
        return True

    return False
