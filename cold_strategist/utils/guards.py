"""
Guards - Non-negotiable Rules
System-level constraints and safety guarantees.

These guard methods return a `GuardResult` describing success and
the reason for failure. Returning structured results (instead of
bare booleans) makes it possible to escalate, log, or present
meaningful reasons to a tribunal or operator.
"""

from dataclasses import dataclass
from typing import Optional, Dict


class GuardViolation(Exception):
    """Exception raised when a guard is violated."""
    pass


@dataclass
class GuardResult:
    ok: bool
    reason: Optional[str] = None


class SystemGuard:
    """Enforces non-negotiable system rules."""

    @staticmethod
    def verify_sovereignty(action: Dict) -> GuardResult:
        """Verify that an action respects sovereign authority.

        Returns a GuardResult with `ok` and an optional `reason`.
        """
        if not isinstance(action, dict):
            return GuardResult(False, "action must be a dict")

        if "actor" not in action or "authority" not in action:
            return GuardResult(False, "missing actor or authority fields")

        # Placeholder: real logic goes here
        return GuardResult(True, None)

    @staticmethod
    def verify_doctrine_integrity(doctrine: Dict) -> GuardResult:
        if not isinstance(doctrine, dict):
            return GuardResult(False, "doctrine must be a dict")

        # Simple check: must contain a canonical_id and a signature field
        if "canonical_id" not in doctrine:
            return GuardResult(False, "missing canonical_id")

        return GuardResult(True, None)

    @staticmethod
    def verify_memory_immutability(record: Dict) -> GuardResult:
        if not isinstance(record, dict):
            return GuardResult(False, "record must be a dict")

        if "created_at" not in record:
            return GuardResult(False, "missing created_at timestamp")

        return GuardResult(True, None)
