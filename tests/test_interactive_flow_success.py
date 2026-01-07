import pytest

from cold_strategist.core.interactive import run_interactive_decision


pytestmark = pytest.mark.policy


class DummyMinister:
    output_shape = {"required_fields": [
        "identity.domain",
        "risk_profile.hard_loss_cap_percent",
        "constraints.irreversibility",
        "meta.emotional_state",
        "meta.prior_patterns",
    ]}


def test_interactive_flow_success(monkeypatch):
    # Monkeypatch Gatekeeper in ContextBuilder to always allow
    from cold_strategist.context import context_builder as cb_mod

    class AlwaysAllow:
        def __init__(self, decision_id):
            self.decision_id = decision_id

        def can_ask(self, request, context_state, active_required_fields, active_ministers):
            return {"status": "ALLOWED"}

        def record_rejection(self, request, reason):
            return None

    monkeypatch.setattr(cb_mod, "Gatekeeper", AlwaysAllow)

    answers = {
        "What kind of situation is this? (relationship, career, conflict, money, identity, other)": "business",
        "What is the worst realistic outcome if nothing changes? (And how bad is that?)": "I could lose my investment",
        "If you choose wrong, can this be undone without lasting damage? (yes/no)": "yes",
        "What emotion is strongest right now? (fear, anger, shame, regret, confusion, something else)": "concerned",
        "Have you faced something structurally similar before? (Describe briefly or 'never')": "never",
    }

    def ask_fn(q):
        return answers.get(q, "never")

    res = run_interactive_decision("Situation described", {"risk": DummyMinister()}, ask_fn)
    assert res["status"] == "CONTEXT_READY"
    assert isinstance(res.get("context_json"), dict)
    # confidence should be >= threshold inside produced context
    conf = res["context_json"]["confidence_map"]["overall_context_confidence"]
    assert conf >= 0.75
