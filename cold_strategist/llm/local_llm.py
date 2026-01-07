"""
Local LLM Implementation
Ollama / LM Studio / llama.cpp integration.
"""

from .interface import LLMInterface


class LocalLLM(LLMInterface):
    """Local LLM implementation for offline operation."""

    def __init__(self, model_name: str = "default"):
        """Initialize the local LLM.
        
        Args:
            model_name: Name of the model to use
        """
        # Default to Claude Haiku 4.5 for local clients
        self.model_name = model_name or "claude/haiku-4.5"

    def generate(self, prompt: str, context: dict = None) -> str:
        """Generate a response using local LLM."""
        pass

    def analyze(self, text: str, analysis_type: str) -> dict:
        """Analyze text using local LLM."""
        pass
