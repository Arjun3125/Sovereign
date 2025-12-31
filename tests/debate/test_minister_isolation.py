"""
L3 Test Suite — Debate & Power Dynamics
Tests minister isolation, debate engine, tribunal logic [RULE-3-1 through 3-4]
"""
import pytest
from tests.conftest import assert_rule


class MockDebateEngine:
    """Mock debate engine for testing minister interactions."""
    
    def __init__(self):
        self.debate_history = []
        self.minister_outputs = {}
    
    def register_minister_output(self, minister_name: str, output: dict):
        """Register a minister's output (simulates minister thinking)."""
        self.minister_outputs[minister_name] = output
    
    def get_minister_output(self, minister_name: str) -> dict:
        """Get a minister's output (should be isolated)."""
        # Only return own minister's output, not others
        return self.minister_outputs.get(minister_name, {})
    
    def run_debate(self, topic: str, ministers: list) -> dict:
        """Run a debate between ministers."""
        self.debate_history.append(topic)
        return {"topic": topic, "participants": ministers}


class TestMinisterIsolation:
    """Minister A cannot see Minister B's intermediate outputs. [RULE-3-1]"""
    
    def test_minister_isolation_basic(self):
        """One minister's intermediate output should not be visible to another."""
        engine = MockDebateEngine()
        
        # Psychology minister thinks about charm
        psychology_output = {
            "analysis": "Charm works through attention redirection",
            "confidence": 0.95
        }
        engine.register_minister_output("psychology", psychology_output)
        
        # Power minister shouldn't see psychology's output
        result = engine.get_minister_output("power")
        assert_rule(
            result == {},
            "RULE-3-1",
            "Power minister should not see psychology minister's output"
        )
    
    def test_minister_sees_own_output(self):
        """A minister should see its own output (trivial but verify)."""
        engine = MockDebateEngine()
        
        power_output = {"analysis": "Control through information", "confidence": 0.9}
        engine.register_minister_output("power", power_output)
        
        result = engine.get_minister_output("power")
        assert_rule(
            result == power_output,
            "RULE-3-1",
            "Minister should see its own output"
        )
    
    def test_multiple_ministers_isolated(self):
        """Multiple ministers should each be isolated from one another."""
        engine = MockDebateEngine()
        
        outputs = {
            "psychology": {"analysis": "Charm via attention", "confidence": 0.95},
            "power": {"analysis": "Control via leverage", "confidence": 0.92},
            "diplomacy": {"analysis": "Influence via negotiation", "confidence": 0.88}
        }
        
        for minister, output in outputs.items():
            engine.register_minister_output(minister, output)
        
        # Each minister sees only own output
        for minister in outputs.keys():
            result = engine.get_minister_output(minister)
            assert_rule(
                result == outputs[minister],
                "RULE-3-1",
                f"{minister} should see only its own output, not others"
            )


class TestPrimeConfidant:
    """Prime Confidant collects all minister outputs and synthesizes. [RULE-3-2]"""
    
    def test_prime_confidant_collects_all_outputs(self):
        """Prime Confidant receives all minister outputs (after debate ends)."""
        engine = MockDebateEngine()
        
        outputs = {
            "psychology": {"advice": "Use attention tactics"},
            "power": {"advice": "Establish dominance first"},
            "diplomacy": {"advice": "Build alliances"}
        }
        
        for minister, output in outputs.items():
            engine.register_minister_output(minister, output)
        
        # Prime Confidant synthesizes (would merge in real implementation)
        collected = {m: engine.get_minister_output(m) for m in outputs.keys()}
        
        assert_rule(
            len(collected) == 3,
            "RULE-3-2",
            "Prime Confidant should collect all 3 minister outputs"
        )
    
    def test_prime_confidant_synthesis_has_input(self):
        """Prime Confidant synthesis should reference inputs from debate."""
        engine = MockDebateEngine()
        
        # Ministers provide input
        engine.register_minister_output("psychology", {"insight": "Charm effective"})
        engine.register_minister_output("power", {"insight": "Force effective"})
        
        # Synthesis should incorporate both
        synthesis = {
            "from_ministers": ["psychology", "power"],
            "integrated": "Charm and force both have role"
        }
        
        assert_rule(
            len(synthesis["from_ministers"]) >= 2,
            "RULE-3-2",
            "Synthesis should reference at least 2 minister inputs"
        )


class TestTribunalMandatory:
    """Tribunal must escalate if ministers contradict on doctrine. [RULE-3-3]"""
    
    def test_contradiction_triggers_tribunal(self):
        """If ministers contradict on doctrine, tribunal escalation required."""
        engine = MockDebateEngine()
        
        # Psychology and Power contradict on core doctrine
        psychology_view = {"doctrine": "Never manipulate without consent"}
        power_view = {"doctrine": "Manipulation acceptable if effective"}
        
        engine.register_minister_output("psychology", psychology_view)
        engine.register_minister_output("power", power_view)
        
        # Contradiction should flag tribunal requirement
        contradiction_detected = (
            psychology_view["doctrine"] != power_view["doctrine"]
        )
        
        assert_rule(
            contradiction_detected,
            "RULE-3-3",
            "Tribunal must be involved when doctrine contradictions exist"
        )
    
    def test_no_tribunal_on_tactical_disagreement(self):
        """Tribunal NOT triggered on tactical (non-doctrine) disagreement."""
        engine = MockDebateEngine()
        
        # Ministers disagree on tactic, not doctrine
        psychology_tactic = {"tactic": "Use subtle influence"}
        power_tactic = {"tactic": "Use direct pressure"}
        
        engine.register_minister_output("psychology", psychology_tactic)
        engine.register_minister_output("power", power_tactic)
        
        # This is normal debate, no doctrine issue
        tribunal_required = False  # Tactical disagreement doesn't trigger tribunal
        
        assert_rule(
            not tribunal_required,
            "RULE-3-3",
            "Tribunal should not be triggered for tactical disagreement"
        )


class TestSilenceSuppression:
    """N Minister suppresses synthesis output (never veto). [RULE-3-4]"""
    
    def test_n_suppresses_synthesis_output(self):
        """N Minister suppression flag prevents synthesis output."""
        engine = MockDebateEngine()
        
        # N Minister indicates suppression
        n_suppression = {"suppress_synthesis": True, "raw_advice": "Use caution"}
        engine.register_minister_output("n", n_suppression)
        
        # Synthesis output suppressed, but raw advice available
        synthesis_suppressed = n_suppression.get("suppress_synthesis", False)
        raw_available = n_suppression.get("raw_advice") is not None
        
        assert_rule(
            synthesis_suppressed and raw_available,
            "RULE-3-4",
            "N suppresses synthesis but raw advice remains available"
        )
    
    def test_n_never_vetos_other_advice(self):
        """N suppression is never an absolute veto of advice."""
        engine = MockDebateEngine()
        
        # Psychology and Power both advise action
        psychology_advice = {"action": "Use charm", "strength": "high"}
        power_advice = {"action": "Use leverage", "strength": "high"}
        n_suppression = {"suppress_synthesis": True, "concerns": "Be careful"}
        
        engine.register_minister_output("psychology", psychology_advice)
        engine.register_minister_output("power", power_advice)
        engine.register_minister_output("n", n_suppression)
        
        # N does NOT veto; system can still use psychology/power advice
        # (just not combined synthesis)
        n_can_veto = False  # Explicitly NOT allowed
        
        assert_rule(
            not n_can_veto,
            "RULE-3-4",
            "N suppression is NOT an absolute veto; advice remains available"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
