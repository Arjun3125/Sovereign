import time
import random
from dataclasses import dataclass
from typing import Optional


LLMStatus = ("OK", "EMPTY", "ERROR", "REFUSED")


@dataclass
class LLMResult:
    status: str
    content: Optional[str]
    parsed: Optional[dict]
    model: Optional[str] = "mock"
    temperature: float = 0.0
    retries: int = 0
    failure_reason: Optional[str] = None


def generate(prompt: str, *, allow_retry: bool = False) -> LLMResult:
    # simulate inference time
    time.sleep(random.uniform(0.3, 0.8))

    parsed = {
        "principles": [
            "Authority depends on perception",
            "Visibility creates vulnerability",
        ],
        "claims": ["Public power invites resistance"],
        "rules": ["Exercise power indirectly when legitimacy is weak"],
        "warnings": ["Excess secrecy erodes trust"],
        "cross_references": [],
    }

    return LLMResult(status="OK", content=str(parsed), parsed=parsed)


def call_llm(prompt: str) -> dict:
    res = generate(prompt)
    if res.status != "OK":
        raise RuntimeError(f"Mock LLM failure: {res.status}")
    return res.parsed
