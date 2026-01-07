"""
LLM client for Ingestion v2.

Handles Ollama HTTP calls with streaming JSON aggregation.
Deterministic: temp=0, top_p=1.
"""

import os
import json
import time
import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1-abliterated:8b")
TIMEOUT = 600


class LLMError(Exception):
    """LLM call failed after retries."""
    pass


def call_llm(prompt: str, model: str = None) -> dict:
    """
    Call Ollama LLM via /api/chat and extract JSON response.

    Args:
        prompt: Full prompt (system + user)
        model: Model name (default: env OLLAMA_MODEL)

    Returns:
        Parsed JSON dict from LLM response

    Raises:
        LLMError: On JSON parsing or HTTP failure
    """
    if model is None:
        model = OLLAMA_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "top_p": 1,
            "top_k": 0,
            "seed": 42
        }
    }

    for attempt in range(2):
        try:
            r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
            r.raise_for_status()

            data = r.json()
            text = data["message"]["content"]

            # Extract JSON from markdown fences if needed
            if "```" in text:
                start = text.index("```") + 3
                if text[start:start+4] == "json":
                    start += 4
                end = text.rindex("```")
                text = text[start:end]

            # Find JSON object
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])

        except Exception as e:
            if attempt == 1:
                raise LLMError(f"LLM call failed: {e}")
            time.sleep(5)
