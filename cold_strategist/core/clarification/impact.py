from typing import Any, Dict


def _get_val(obj: Any, key: str, default=0.0):
    # support dicts and objects with attributes
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def compute_impact(before: Any, after: Any) -> Dict[str, Any]:
    return {
        "clarity_delta": float(_get_val(after, "clarity", 0.0)) - float(_get_val(before, "clarity", 0.0)),
        "emotion_delta": float(_get_val(after, "emotional_load", 0.0)) - float(_get_val(before, "emotional_load", 0.0)),
        "resolution_changed": _get_val(before, "resolution") != _get_val(after, "resolution"),
    }
