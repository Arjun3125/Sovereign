"""LLM package exports.

Provides a convenience `call_llm` wrapper for backward compatibility and
exports `LLMGateway` for explicit usage.
"""
from .gateway import LLMGateway, call_llm

__all__ = ["LLMGateway", "call_llm"]
