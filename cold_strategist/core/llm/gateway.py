from typing import Any, Optional
import os
import logging
import requests

from .ollama_client import OllamaClient
from .profiles import LLM_PROFILES
from .guardrails import build_system_prompt

logger = logging.getLogger(__name__)


class LLMGateway:
    def __init__(self, model: Optional[str] = None):
        # If caller doesn't provide a model, OllamaClient will load the
        # reasoning/default model from config.
        self.client = OllamaClient(model=model)

    def run(
        self,
        prompt: str,
        *,
        profile: str = "default",
        war_mode: bool = False,
        require_evidence: bool = False,
        system: str = None,
        task: str = None,
    ) -> str:
        cfg = LLM_PROFILES.get(profile, LLM_PROFILES["default"])

        # allow callers to pass a `system` override (legacy callers pass SYSTEM)
        system_prompt = system if system is not None else build_system_prompt(
            war_mode=war_mode, require_evidence=require_evidence
        )

        try:
            return self.client.generate(
                prompt=prompt,
                task=task,
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                system=system_prompt,
            )
        except requests.RequestException as exc:
            logger.warning("LLM request failed: %s", exc)
            # deterministic fallback
            return "[LLM_UNAVAILABLE]"


# default global gateway used by convenience function below
_default_gateway = LLMGateway()


def call_llm(*args, **kwargs) -> Any:
    """Compatibility wrapper.

    Supports both modern `call_llm(prompt, profile=..., war_mode=...)` and legacy
    `call_llm(system=..., user=...)` where `user` becomes the prompt and `system`
    is passed through as the system prompt.
    """
    # legacy form: call_llm(system=SYSTEM, user=text)
    if "user" in kwargs and "prompt" not in kwargs and len(args) == 0:
        prompt = kwargs.pop("user")
        system = kwargs.pop("system", None)
        return _default_gateway.run(prompt, system=system, **kwargs)

    # positional prompt
    if len(args) > 0:
        prompt = args[0]
        return _default_gateway.run(prompt, **kwargs)

    # named prompt
    prompt = kwargs.pop("prompt", None)
    if prompt is None:
        raise TypeError("call_llm requires a prompt (positional or 'user'/'prompt' kwarg)")
    return _default_gateway.run(prompt, **kwargs)
