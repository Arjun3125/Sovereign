"""
Test Foundation & Assertion Helpers
Implements rule-aware testing infrastructure
"""
import pytest
from typing import Any, List


class RuleViolationError(AssertionError):
    """Custom assertion error that includes rule reference."""
    
    def __init__(self, rule_id: str, message: str):
        self.rule_id = rule_id
        self.message = message
        super().__init__(f"VIOLATION [{rule_id}]: {message}")


def assert_rule(condition: bool, rule_id: str, message: str) -> None:
    """
    Assert a condition and reference the constitutional rule being tested.
    
    Args:
        condition: Boolean to assert True
        rule_id: Rule identifier (e.g., "RULE-1-5")
        message: Human-readable explanation of what failed
        
    Raises:
        RuleViolationError: If condition is False
    """
    if not condition:
        raise RuleViolationError(rule_id, message)


def assert_approximately_equal(value: float, expected: float, tolerance: float = 0.001, 
                                rule_id: str = "RULE-X-X", message: str = "") -> None:
    """
    Assert floating-point values are approximately equal.
    
    Args:
        value: Actual value
        expected: Expected value
        tolerance: Acceptable difference (default 0.001)
        rule_id: Constitutional rule
        message: Error message
    """
    assert_rule(
        abs(value - expected) <= tolerance,
        rule_id,
        f"{message}. Expected {expected} ± {tolerance}, got {value}"
    )


def assert_subset(actual: set, required: set, rule_id: str, message: str) -> None:
    """Assert all required elements are in actual set."""
    missing = required - actual
    assert_rule(
        len(missing) == 0,
        rule_id,
        f"{message}. Missing elements: {missing}"
    )


def assert_no_overlap(set_a: set, set_b: set, rule_id: str, message: str) -> None:
    """Assert two sets have no overlap (for domain isolation, etc)."""
    overlap = set_a & set_b
    assert_rule(
        len(overlap) == 0,
        rule_id,
        f"{message}. Overlap found: {overlap}"
    )


@pytest.fixture
def sample_embeddings():
    """Fixture: sample embeddings for testing similarity."""
    return {
        "identical": [0.5] * 768,  # All same value
        "orthogonal": [0.5] * 384 + [-0.5] * 384,  # Opposite halves
        "similar": [0.5] * 767 + [0.501],  # Nearly identical
    }


@pytest.fixture
def sample_principles():
    """Fixture: sample principles for retriever tests."""
    return [
        {
            "principle_id": "charm_001",
            "principle": "Charm lowers defenses by redirecting attention",
            "confidence_weight": 0.85,
            "domain_fit": ["psychology", "persuasion"],
            "embedding": [0.1] * 768,
            "source": {"book": "art_of_seduction", "chapter": "raw"}
        },
        {
            "principle_id": "charm_002",
            "principle": "Listening builds trust faster than talking",
            "confidence_weight": 0.85,
            "domain_fit": ["psychology", "diplomacy"],
            "embedding": [0.12] * 768,
            "source": {"book": "art_of_seduction", "chapter": "raw"}
        },
        {
            "principle_id": "power_001",
            "principle": "Make people feel like they're losing standing to gain power",
            "confidence_weight": 0.85,
            "domain_fit": ["power"],
            "embedding": [0.2] * 768,
            "source": {"book": "48_laws_of_power", "chapter": "raw"}
        },
        {
            "principle_id": "power_002",
            "principle": "Silence compounds authority",
            "confidence_weight": 0.7,
            "domain_fit": ["power"],
            "embedding": [0.22] * 768,
            "source": {"book": "48_laws_of_power", "chapter": "raw"}
        },
    ]


if __name__ == "__main__":
    print("Testing framework loaded. Run with: pytest tests/")
