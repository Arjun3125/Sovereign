"""Phase-2 guard: placeholder for additional safety checks."""

def guard_output(minister_id: str, output: dict) -> bool:
    """Return True if output passes guard checks."""
    # Minimal conservative guard: require dict or silence
    if not output:
        return True
    if not isinstance(output, dict):
        return False
    return True
