import os
import json
import requests
from typing import Optional


def call_llm(prompt: str, model: Optional[str] = None, timeout: int = 30) -> str:
    """Call a local LLM (Ollama) using environment variables.

    Expects `OLLAMA_URL` and `OLLAMA_MODEL` (or `model` arg) to be set.
    Falls back to raising a RuntimeError with an explanatory message.
    """
    ollama_url = os.getenv("OLLAMA_URL")
    ollama_model = model or os.getenv("OLLAMA_MODEL")

    if not ollama_url or not ollama_model:
        raise RuntimeError(
            "No LLM configured. Set OLLAMA_URL and OLLAMA_MODEL environment variables."
        )

    endpoint = ollama_url.rstrip("/") + "/api/generate"
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "temperature": 0,
        "top_p": 1,
        "top_k": 0,
        "max_tokens": 1024,
    }

    with requests.post(endpoint, json=payload, timeout=timeout, stream=True) as resp:
        resp.raise_for_status()

        # Ollama often streams newline-delimited JSON objects with a 'response' field.
        parts = []
        try:
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                # Some servers send comma-separated chunks; try to parse JSON per line
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and "response" in obj:
                        parts.append(obj.get("response", ""))
                    elif isinstance(obj, dict) and "text" in obj:
                        parts.append(obj.get("text", ""))
                    else:
                        # Unexpected structure: append the raw line
                        parts.append(line)
                except json.JSONDecodeError:
                    # If line isn't JSON, append as-is
                    parts.append(line)
        except Exception:
            # Fallback to full body if streaming iteration fails
            return resp.text

        return "".join(parts)
