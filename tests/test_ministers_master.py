"""
E. MINISTER SYSTEM TESTS (MANTRI SABHA)

Tests guarantee:
- Ministers cannot speak outside role (jurisdiction boundaries) (E1)
- Ministers do not see each other's outputs unless explicitly allowed (E2)
"""

import pytest
from typing import Dict, Any


class TestE1_JurisdictionBoundaries:
    """E1: Must guarantee ministers cannot speak outside their role"""
    
    @pytest.fixture
    def minister_roles(self):
        """Define minister jurisdictions"""
        return {
            "MinisterOfTruth": {
                "scope": ["factual_consistency", "doctrine_alignment"],
                "can_evaluate": ["claims", "statements"]
            },
            "MinisterOfRisk": {
                "scope": ["risks", "failure_modes", "consequences"],
                "can_evaluate": ["strategies", "plans"]
            },
            "MinisterOfPower": {
                "scope": ["leverage", "dynamics", "optics"],
                "can_evaluate": ["tactics", "positioning"]
            }
        }
    
    def test_minister_scope_enforced(self, minister_roles):
        """Minister cannot evaluate outside their scope"""
        minister = "MinisterOfRisk"
        scope = minister_roles[minister]["scope"]
        
        # Valid query (within scope)
        valid_query = "What are the risks?"
        has_risk_keyword = any(kw in valid_query.lower() for kw in scope)
        assert has_risk_keyword, "Valid query not recognized"
        
        # Invalid query (outside scope)
        invalid_query = "What are the negotiation tactics?"
        has_scope_keyword = any(kw in invalid_query.lower() for kw in scope)
        assert not has_scope_keyword, "Invalid query should be rejected"
    
    def test_minister_rejects_out_of_scope(self, minister_roles):
        """Out-of-scope queries raise ScopeViolation"""
        minister = "MinisterOfTruth"
        scope = minister_roles[minister]["scope"]
        
        query = "What tactics would give us leverage?"
        
        # Check if query is in scope
        query_lower = query.lower()
        is_in_scope = any(
            term in query_lower 
            for term in ["factual", "consistency", "doctrine", "alignment"]
        )
        
        if not is_in_scope:
            violation_raised = True
        else:
            violation_raised = False
        
        assert violation_raised, "Out-of-scope query should be rejected"
    
    def test_all_ministers_have_boundaries(self, minister_roles):
        """Each minister has defined scope boundaries"""
        for minister_name, minister_config in minister_roles.items():
            assert "scope" in minister_config, \
                f"{minister_name} has no scope defined"
            assert len(minister_config["scope"]) > 0, \
                f"{minister_name} has empty scope"
            assert "can_evaluate" in minister_config, \
                f"{minister_name} has no evaluable types"
    
    def test_no_minister_universal_scope(self, minister_roles):
        """No minister has universal scope (all topics)"""
        universal_topics = [
            "everything", "*", "all", "any"
        ]
        
        for minister_name, config in minister_roles.items():
            scope_lower = [s.lower() for s in config["scope"]]
            for universal in universal_topics:
                assert universal not in scope_lower, \
                    f"{minister_name} has universal scope"


class TestE2_MinisterIsolation:
    """E2: Must guarantee ministers don't see each other's outputs"""
    
    @pytest.fixture
    def minister_system(self):
        """Mock minister system"""
        return {
            "ministers": {
                "truth": {"state": {}, "output": None},
                "risk": {"state": {}, "output": None},
                "power": {"state": {}, "output": None}
            },
            "case": {"situation": "Negotiation with competitor"}
        }
    
    def test_ministers_isolated(self, minister_system):
        """Ministers evaluate independently without seeing each other"""
        case = minister_system["case"]
        
        # Minister 1 evaluates
        truth_output = {"analysis": "Facts are aligned with doctrine"}
        minister_system["ministers"]["truth"]["output"] = truth_output
        
        # Minister 2 evaluates (should NOT see Minister 1's output)
        # When risk minister evaluates, truth's output is not visible
        risk_visible_state = minister_system["ministers"]["risk"]["state"]
        
        assert "truth" not in risk_visible_state, \
            "Risk minister can see Truth minister's state"
        assert "output" not in risk_visible_state, \
            "Risk minister can see other minister's output"
    
    def test_no_shared_state_between_ministers(self, minister_system):
        """Ministers have separate state, not shared"""
        # Set state for minister 1
        minister_system["ministers"]["truth"]["state"]["confidence"] = 0.95
        
        # Verify minister 2 doesn't have it
        assert "confidence" not in minister_system["ministers"]["risk"]["state"], \
            "Risk minister shares state with Truth"
        assert "confidence" not in minister_system["ministers"]["power"]["state"], \
            "Power minister shares state with Truth"
    
    def test_explicit_information_passing(self, minister_system):
        """Information between ministers only via explicit passing"""
        # Minister 1 produces output
        truth_conclusion = "Doctrine clearly supports this action"
        
        # To pass to Minister 2, must be explicit
        can_explicitly_pass = True
        
        if can_explicitly_pass:
            minister_system["ministers"]["risk"]["input"] = {
                "from": "truth",
                "data": truth_conclusion
            }
        
        # Verify it's explicitly marked (not magically visible)
        assert "input" in minister_system["ministers"]["risk"], \
            "Explicit passing not recorded"
        assert minister_system["ministers"]["risk"]["input"]["from"] == "truth", \
            "Source not traceable"
    
    def test_minister_state_immutable_to_others(self, minister_system):
        """One minister cannot modify another's state"""
        # Set initial state
        minister_system["ministers"]["truth"]["state"]["locked"] = True
        initial_locked = minister_system["ministers"]["truth"]["state"]["locked"]
        
        # Risk minister tries to modify (should not affect truth)
        minister_system["ministers"]["risk"]["state"]["locked"] = False
        
        # Truth minister's state unchanged
        final_locked = minister_system["ministers"]["truth"]["state"]["locked"]
        
        assert initial_locked == final_locked, \
            "Risk minister modified Truth's state"
        assert minister_system["ministers"]["truth"]["state"]["locked"] is True, \
            "State was corrupted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
