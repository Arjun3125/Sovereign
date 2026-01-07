from typing import Dict, Any

ALLOWED_STANCES = {
    "ADVANCE",
    "DELAY",
    "AVOID",
    "CONDITIONAL",
    "STOP",
    "NEEDS_DATA",
    "ABSTAIN",
}

REQUIRED_KEYS = {
    "minister",
    "stance",
    "justification",
    "constraints",
    "risks",
    "confidence",
    "citations",
}


def validate_minister_output(
    output: Dict[str, Any],
    retrieved_doctrine_ids: set,
) -> None:
    # 1. Structural validation
    if not isinstance(output, dict):
        raise ValueError("Output is not a JSON object")

    missing = REQUIRED_KEYS - set(output.keys())
    if missing:
        raise ValueError(f"Missing keys: {missing}")

    # 2. Stance validation
    if output["stance"] not in ALLOWED_STANCES:
        raise ValueError(f"Invalid stance: {output['stance']}")

    # 3. Confidence validation
    confidence = output["confidence"]
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        raise ValueError("Confidence must be between 0 and 1")

    # 4. Justification validation
    if not isinstance(output["justification"], list):
        raise ValueError("Justification must be a list")

    used_doctrines = set()
    for j in output["justification"]:
        if "doctrine_id" not in j or "reason" not in j:
            raise ValueError("Invalid justification entry")
        used_doctrines.add(j["doctrine_id"])

    # 5. Doctrine grounding enforcement
    if not used_doctrines.issubset(retrieved_doctrine_ids):
        raise ValueError("Justification uses non-retrieved doctrine")

    # 6. Deduplication enforcement
    if len(used_doctrines) < len(output["justification"]):
        raise ValueError("Duplicate doctrine usage detected")

    # 7. Risk / constraint sanity
    if not isinstance(output["constraints"], list):
        raise ValueError("Constraints must be a list")
    if not isinstance(output["risks"], list):
        raise ValueError("Risks must be a list")

    # 8. Citation validation
    for c in output["citations"]:
        if "doctrine_id" not in c:
            raise ValueError("Citation missing doctrine_id")
        if c["doctrine_id"] not in retrieved_doctrine_ids:
            raise ValueError("Citation references unknown doctrine")

    # 9. Hard rule: STOP / NEEDS_DATA must have no ADVANCE language
    if output["stance"] in {"STOP", "NEEDS_DATA"}:
        if output["confidence"] > 0.6:
            raise ValueError("High confidence not allowed for STOP / NEEDS_DATA")

    return None  # Valid
