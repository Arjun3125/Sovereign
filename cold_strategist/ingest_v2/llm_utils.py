import json
import re
from typing import Any, Dict


def extract_json_block(text: str) -> Dict[str, Any]:
    """
    Extract the first JSON object found in text and return it as a dict.

    Tries direct json.loads first; if that fails, searches for the first {...}
    block and attempts to parse that. Raises ValueError on failure.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # fallback: find a {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in text")

    block = match.group(0)
    try:
        return json.loads(block)
    except json.JSONDecodeError as e:
        raise ValueError(f"Found JSON-like block but failed to parse: {e}")
