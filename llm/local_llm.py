"""
Local LLM Implementation
Ollama / LM Studio / llama.cpp integration.
"""

import json
from .interface import LLMInterface


class LocalLLM(LLMInterface):
    """Local LLM implementation for offline operation."""

    def __init__(self, model_name: str = "default"):
        """Initialize the local LLM.
        
        Args:
            model_name: Name of the model to use
        """
        self.model_name = model_name

    def generate(self, prompt: str, context: dict = None) -> str:
        """Generate a response using local LLM.

        If no real backend is connected, returns a dummy JSON response
        suitable for the synthesis engine to prevent crashes during testing.
        """
        # TODO: Connect to real local LLM backend (Ollama, LM Studio)

        # Fallback dummy response for testing/initial wiring
        return json.dumps({
            "aligned_with_goal": True,
            "advice": "Proceed with caution using available resources.",
            "rationale": "This is a placeholder response from LocalLLM.",
            "counter_patterns": ["Overconfidence", "Lack of planning"],
            "clarifying_questions": [],
            "citations": [],
            "confidence": 0.7
        })

    def analyze(self, text: str, analysis_type: str) -> dict:
        """Analyze text using local LLM."""
        return {"status": "mock_analysis", "text": text}
