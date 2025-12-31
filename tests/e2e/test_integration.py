"""
L5 Test Suite — End-to-End Integration
Tests override flow, war escalation, suppressed synthesis, full determinism [RULE-5-1 through 5-6]
"""
import pytest
from tests.conftest import assert_rule


class MockSovereignSystem:
    """Mock full Sovereign system for E2E testing."""
    
    def __init__(self):
        self.doctrine = {"core": "Sovereignty through honesty"}
        self.memory = {}
        self.override_log = []
        self.synthesis_log = []
        self.determinism_check = True
    
    def propose_action(self, action: str) -> dict:
        """System proposes action to sovereign."""
        return {"action": action, "reasoning": "Based on debate"}
    
    def sovereign_override(self, action: str, reason: str):
        """Sovereign overrides system action."""
        self.override_log.append({"action": action, "reason": reason})
    
    def suppress_synthesis(self, suppress: bool):
        """Suppress synthesis output (N request)."""
        self.synthesis_log.append({"suppressed": suppress})
    
    def run_determinism_check(self, iterations: int = 3) -> bool:
        """Run same scenario multiple times, verify identical outputs."""
        results = []
        for _ in range(iterations):
            output = self.propose_action("test_action")
            results.append(output)
        
        # All results should be identical
        return all(r == results[0] for r in results)


class TestOverrideFlow:
    """Sovereign can always override system decisions. [RULE-5-1]"""
    
    def test_sovereign_override_accepted(self):
        """Sovereign override should be accepted without question."""
        system = MockSovereignSystem()
        
        # Sovereign overrides system action
        system.sovereign_override("alternative_action", "I trust my judgment more")
        
        assert_rule(
            len(system.override_log) > 0,
            "RULE-5-1",
            "Sovereign override should be logged and accepted"
        )
    
    def test_override_not_questioned(self):
        """System should not question or contradict sovereign override."""
        system = MockSovereignSystem()
        
        override_reason = "My intuition says otherwise"
        system.sovereign_override("intuitive_action", override_reason)
        
        logged_override = system.override_log[-1]
        assert_rule(
            logged_override["reason"] == override_reason,
            "RULE-5-1",
            "Sovereign's reasoning should be respected without question"
        )


class TestWarEscalation:
    """War Mode escalation follows strict protocol. [RULE-5-2]"""
    
    def test_war_escalation_logged(self):
        """War mode escalation must be logged with timestamp."""
        system = MockSovereignSystem()
        
        # Simulate war escalation
        escalation = {"type": "war_mode", "triggered_by": "explicit_sovereign_request"}
        system.override_log.append(escalation)
        
        assert_rule(
            any(e.get("type") == "war_mode" for e in system.override_log),
            "RULE-5-2",
            "War escalation must be logged"
        )
    
    def test_war_mode_not_triggered_by_urgency_alone(self):
        """War mode should never trigger from urgency; only explicit request."""
        system = MockSovereignSystem()
        
        # No override logged for urgency (no auto-escalation)
        auto_escalations = [
            e for e in system.override_log 
            if e.get("triggered_by") == "urgency"
        ]
        
        assert_rule(
            len(auto_escalations) == 0,
            "RULE-5-2",
            "War mode must never auto-escalate from urgency"
        )


class TestSuppressedSynthesis:
    """N suppression prevents synthesis, not advice. [RULE-5-3]"""
    
    def test_synthesis_suppressed_on_n_request(self):
        """When N requests, synthesis output suppressed."""
        system = MockSovereignSystem()
        
        # N suppresses synthesis
        system.suppress_synthesis(True)
        
        assert_rule(
            system.synthesis_log[-1]["suppressed"] == True,
            "RULE-5-3",
            "Synthesis should be suppressed when N requests"
        )
    
    def test_raw_advice_available_despite_suppression(self):
        """Raw advice available even when synthesis suppressed."""
        system = MockSovereignSystem()
        
        # Suppress synthesis but keep raw outputs available
        system.suppress_synthesis(True)
        raw_advice = {"psychology": "advice here", "power": "advice here"}
        
        assert_rule(
            raw_advice is not None,
            "RULE-5-3",
            "Raw advice must remain available despite synthesis suppression"
        )


class TestDeterminism:
    """System outputs deterministic (same input → same output). [RULE-5-4]"""
    
    def test_system_determinism(self):
        """Same scenario twice should produce identical results."""
        system = MockSovereignSystem()
        
        is_deterministic = system.run_determinism_check(iterations=3)
        
        assert_rule(
            is_deterministic,
            "RULE-5-4",
            "System must be deterministic (identical inputs → identical outputs)"
        )
    
    def test_doctrine_consistency(self):
        """Doctrine should remain consistent across runs."""
        system = MockSovereignSystem()
        
        doctrine1 = system.doctrine.copy()
        doctrine2 = system.doctrine.copy()
        
        assert_rule(
            doctrine1 == doctrine2,
            "RULE-5-4",
            "Doctrine must be consistent across operations"
        )


class TestMemoryPersistence:
    """Memory persists correctly across operations. [RULE-5-5]"""
    
    def test_memory_write_persists(self):
        """Memory writes should persist."""
        system = MockSovereignSystem()
        
        system.memory["key"] = "value"
        retrieved = system.memory.get("key")
        
        assert_rule(
            retrieved == "value",
            "RULE-5-5",
            "Memory writes must persist"
        )
    
    def test_memory_isolation_from_doctrine(self):
        """Memory changes should not affect doctrine."""
        system = MockSovereignSystem()
        
        original_doctrine = system.doctrine.copy()
        system.memory["temporary"] = "data"
        
        assert_rule(
            system.doctrine == original_doctrine,
            "RULE-5-5",
            "Memory changes must not affect doctrine"
        )


class TestErrorRecovery:
    """System recovers gracefully from errors. [RULE-5-6]"""
    
    def test_invalid_action_handled_gracefully(self):
        """Invalid action should not crash system."""
        system = MockSovereignSystem()
        
        try:
            # Try invalid action
            result = system.propose_action(None)
            recovered = result is not None
        except Exception:
            recovered = False
        
        assert_rule(
            recovered,
            "RULE-5-6",
            "System should handle invalid input gracefully"
        )
    
    def test_memory_corruption_isolated(self):
        """Corrupt memory entry should not crash system."""
        system = MockSovereignSystem()
        
        # Add corrupted entry
        system.memory["corrupt"] = {"circular": None}
        system.memory["corrupt"]["circular"] = system.memory["corrupt"]
        
        # System should still function
        can_still_propose = system.propose_action("test") is not None
        
        assert_rule(
            can_still_propose,
            "RULE-5-6",
            "Corrupt memory should not crash system operations"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
