import pytest

from cold_strategist.core.interactive import run_interactive_decision, TERMINATION_STRING


pytestmark = pytest.mark.policy


class DummyMinister:
    output_shape = {"required_fields": ["risk_profile.hard_loss_cap_percent"]}


def test_interactive_flow_termination_on_rejection(monkeypatch):
    # Monkeypatch Gatekeeper in ContextBuilder to allow first then reject
    from cold_strategist.context import context_builder as cb_mod

    state = {"calls": 0}

    class FlakyGK:
        def __init__(self, decision_id):
            self.decision_id = decision_id

        def can_ask(self, request, context_state, active_required_fields, active_ministers):
            state["calls"] += 1
            if state["calls"] == 1:
                return {"status": "ALLOWED"}
            return {"status": "REJECTED", "reason": "TEST_FORCED_REJECT"}

        def record_rejection(self, request, reason):
            return None

    monkeypatch.setattr(cb_mod, "Gatekeeper", FlakyGK)

    # Provide answers that do not improve confidence meaningfully
    def ask_fn(q):
        return ""

    res = run_interactive_decision("Edge case", {"risk": DummyMinister()}, ask_fn, max_rounds=5)
    assert res["status"] == "TERMINATED"
    assert res["payload"] == TERMINATION_STRING
