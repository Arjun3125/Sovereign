"""
LLM Interface
Abstract interface for LLM interactions.
LLM is a tool, not the system.
"""

from abc import ABC, abstractmethod


class LLMInterface(ABC):
    """Abstract interface for LLM interactions."""

    @abstractmethod
    def generate(self, prompt: str, context: dict = None) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            context: Optional context for the generation
            
        Returns:
            The LLM's response
        """
        pass

    @abstractmethod
    def analyze(self, text: str, analysis_type: str) -> dict:
        """Use LLM to analyze text.
        
        Args:
            text: The text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        pass
