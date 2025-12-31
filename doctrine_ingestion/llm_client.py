import json
import os
import time
import requests
from dataclasses import dataclass
from typing import Optional, Literal

_base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_URL = _base_url if _base_url.endswith("/api/generate") else _base_url.rstrip("/") + "/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# Operational knobs
TIMEOUT_SEC = 600  # 10 minutes
RETRY_ONCE = True  # conservative single retry only


LLMStatus = Literal["OK", "EMPTY", "ERROR", "REFUSED"]


@dataclass
class LLMResult:
    status: LLMStatus
    content: Optional[str]
    parsed: Optional[dict]
    model: Optional[str]
    temperature: float
    retries: int = 0
    failure_reason: Optional[str] = None


class LLMError(RuntimeError):
    pass


def _call_ollama_raw(prompt: str, temperature: float = 0.0) -> str:
    # Enforce deterministic defaults regardless of callers
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 1,
            "num_ctx": 32768
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SEC)
    r.raise_for_status()
    return r.json().get("response", "")


def _parse_json_strict(text: str) -> dict:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        raise LLMError(f"Invalid JSON from LLM: {e}\nRAW:\n{text}")


def generate(prompt: str, *, allow_retry: bool = RETRY_ONCE) -> LLMResult:
    """Call the provider and return a structured `LLMResult`.

    This function enforces deterministic generation options and
    distinguishes failure modes so callers can handle them explicitly.
    """
    tries = 0
    while True:
        tries += 1
        try:
            raw = _call_ollama_raw(prompt)
        except Exception as e:
            if allow_retry and tries == 1:
                time.sleep(1)
                continue
            return LLMResult(
                status="ERROR",
                content=None,
                parsed=None,
                model=OLLAMA_MODEL,
                temperature=0.0,
                retries=tries - 1,
                failure_reason=str(e),
            )

        # Minimal refusal detection (provider-specific heuristics could go here)
        if not raw or not raw.strip():
            return LLMResult(status="EMPTY", content=raw, parsed=None, model=OLLAMA_MODEL, temperature=0.0, retries=tries - 1)

        try:
            parsed = _parse_json_strict(raw)
        except LLMError as e:
            # Parsing failed — treat as ERROR but surface raw content
            if allow_retry and tries == 1:
                time.sleep(1)
                continue
            return LLMResult(
                status="ERROR",
                content=raw,
                parsed=None,
                model=OLLAMA_MODEL,
                temperature=0.0,
                retries=tries - 1,
                failure_reason=str(e),
            )

        # Success
        return LLMResult(status="OK", content=raw, parsed=parsed, model=OLLAMA_MODEL, temperature=0.0, retries=tries - 1)


def call_llm(prompt: str) -> dict:
    """Compatibility wrapper: returns parsed dict or raises on failure.

    Upstream ingestion expects a dict. For Sovereign safety we do not
    silently return bad output — we raise so the caller can decide.
    """
    res = generate(prompt)
    if res.status != "OK":
        raise LLMError(f"LLM call failed: status={res.status} reason={res.failure_reason}")
    return res.parsed
