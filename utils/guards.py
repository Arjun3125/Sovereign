"""
Guards - Non-negotiable Rules
System-level constraints and safety guarantees.
"""


class GuardViolation(Exception):
    """Exception raised when a guard is violated."""
    pass


class SystemGuard:
    """Enforces non-negotiable system rules."""

    @staticmethod
    def verify_sovereignty(action: dict) -> bool:
        """Verify that an action respects sovereign authority.
        
        Args:
            action: The action to verify
            
        Returns:
            True if the action is authorized
            
        Raises:
            GuardViolation: If the action violates sovereignty
        """
        pass

    @staticmethod
    def verify_doctrine_integrity(doctrine: dict) -> bool:
        """Verify that a doctrine hasn't been tampered with.
        
        Args:
            doctrine: The doctrine to verify
            
        Returns:
            True if the doctrine is intact
            
        Raises:
            GuardViolation: If doctrine integrity is compromised
        """
        pass

    @staticmethod
    def verify_memory_immutability(record: dict) -> bool:
        """Verify that memory records cannot be retroactively changed.
        
        Args:
            record: The record to verify
            
        Returns:
            True if immutability is maintained
            
        Raises:
            GuardViolation: If immutability is compromised
        """
        pass
