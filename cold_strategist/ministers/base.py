"""
Base Minister Class
Abstract base class for all ministers (perspectives).
"""

from abc import ABC, abstractmethod


class MinisterBase(ABC):
    """Abstract base class for all ministers in the Sovereign council."""

    def __init__(self, name: str):
        """Initialize a minister.
        
        Args:
            name: The minister's name/title
        """
        self.name = name

    @abstractmethod
    def analyze(self, context: dict) -> dict:
        """Analyze a situation from this minister's perspective.
        
        Args:
            context: The current situation context
            
        Returns:
            A dictionary with this minister's analysis
        """
        pass

    @abstractmethod
    def get_doctrine(self) -> dict:
        """Get this minister's immutable doctrine.
        
        Returns:
            The locked doctrine for this minister
        """
        pass
