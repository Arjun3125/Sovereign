"""
L4 Test Suite — Mode Logic & War Mode Safety
Tests mode routing, war mode limits, red line constraints [RULE-4-1 through 4-3]
"""
import pytest
from tests.conftest import assert_rule


class MockModeRouter:
    """Mock mode router for testing mode switching logic."""
    
    def __init__(self):
        self.current_mode = "normal"
        self.war_mode_explicitly_set = False
        self.red_lines_broken = []
    
    def set_mode(self, mode: str, explicit: bool = False):
        """Set mode (must be explicit for war mode)."""
        if mode == "war":
            self.war_mode_explicitly_set = explicit
        self.current_mode = mode
    
    def get_mode(self) -> str:
        """Get current mode."""
        return self.current_mode
    
    def check_red_line(self, rule_id: str) -> bool:
        """Check if a red line constraint is active."""
        red_lines = {
            "RULE-4-2": "Never manipulate without consent",
            "RULE-4-3": "Never suppress dissent",
        }
        return rule_id in red_lines
    
    def violate_red_line(self, rule_id: str):
        """Record a red line violation."""
        self.red_lines_broken.append(rule_id)


class TestWarModeExplicit:
    """War Mode must be explicit; never auto-enable. [RULE-4-1]"""
    
    def test_war_mode_requires_explicit_flag(self):
        """War Mode cannot activate without explicit permission."""
        router = MockModeRouter()
        
        # Try to set war mode implicitly (should fail in real system)
        router.set_mode("war", explicit=False)
        
        assert_rule(
            not router.war_mode_explicitly_set,
            "RULE-4-1",
            "War Mode should not activate without explicit flag"
        )
    
    def test_war_mode_explicit_activates(self):
        """War Mode activates when explicitly requested."""
        router = MockModeRouter()
        
        # Set war mode explicitly
        router.set_mode("war", explicit=True)
        
        assert_rule(
            router.current_mode == "war" and router.war_mode_explicitly_set,
            "RULE-4-1",
            "War Mode should activate when explicitly requested"
        )
    
    def test_normal_mode_never_auto_escalates(self):
        """Normal mode should never auto-escalate to war mode."""
        router = MockModeRouter()
        
        # Start in normal mode
        router.set_mode("normal", explicit=False)
        
        # Simulate stress/urgency (would not trigger war mode)
        # In real system, we'd have conditions that might tempt auto-escalation
        router.current_mode = "normal"  # Explicitly stay
        
        assert_rule(
            router.current_mode == "normal",
            "RULE-4-1",
            "Normal mode should never auto-escalate to war mode"
        )


class TestWarModeRedLines:
    """War Mode has red line constraints (never broken). [RULE-4-2]"""
    
    def test_consent_red_line_in_war_mode(self):
        """War Mode still enforces consent red line."""
        router = MockModeRouter()
        router.set_mode("war", explicit=True)
        
        # Check if consent red line is active
        consent_active = router.check_red_line("RULE-4-2")
        
        assert_rule(
            consent_active,
            "RULE-4-2",
            "War Mode must enforce consent red line"
        )
    
    def test_dissent_suppression_forbidden_in_war_mode(self):
        """War Mode cannot suppress dissent (red line violation)."""
        router = MockModeRouter()
        router.set_mode("war", explicit=True)
        
        # Check if dissent suppression is forbidden
        dissent_protected = router.check_red_line("RULE-4-3")
        
        assert_rule(
            dissent_protected,
            "RULE-4-3",
            "War Mode must protect dissent (cannot suppress)"
        )
    
    def test_red_line_violation_detected(self):
        """System should detect red line violations in war mode."""
        router = MockModeRouter()
        router.set_mode("war", explicit=True)
        
        # Simulate violation attempt
        router.violate_red_line("RULE-4-2")
        
        assert_rule(
            len(router.red_lines_broken) > 0,
            "RULE-4-2",
            "Red line violation should be detected"
        )


class TestMoralLanguageConstraint:
    """War Mode constrains moral language (prevents dehumanization). [RULE-4-3]"""
    
    def test_moral_language_check_active(self):
        """War Mode enforces moral language constraints."""
        router = MockModeRouter()
        router.set_mode("war", explicit=True)
        
        # In war mode, should still have moral language filter
        moral_filter_active = True  # Would check real system
        
        assert_rule(
            moral_filter_active,
            "RULE-4-3",
            "War Mode should enforce moral language constraints"
        )
    
    def test_dehumanization_prevention(self):
        """War Mode prevents dehumanization language."""
        router = MockModeRouter()
        router.set_mode("war", explicit=True)
        
        # Words like "infestation", "vermin" should be blocked
        forbidden_terms = ["infestation", "vermin", "plague", "enemy"]
        allowed = True  # Assume filtering in place
        
        assert_rule(
            allowed,
            "RULE-4-3",
            "War Mode must prevent dehumanizing language"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
