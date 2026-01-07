import pytest

from cold_strategist.core.gatekeeper import Gatekeeper

pytestmark = pytest.mark.policy


def _make_context_with_field(field_path: str):
    # build minimal context with the full path present but empty value
    parts = field_path.split('.')
    state = {}
    node = state
    for i, p in enumerate(parts):
        if i == len(parts) - 1:
            node[p] = {"value": None, "confidence": 0.0, "stable": False}
        else:
            node[p] = {}
            node = node[p]
    return state


def test_required_field_correct_minister_allowed():
    g = Gatekeeper('D-ALLOW-1')
    field = "risk_profile.hard_loss_cap_percent"
    ctx = _make_context_with_field(field)
    active_required_fields = {"risk": [field]}
    active_ministers = ["risk"]
    request = {
        "requester": "risk",
        "requested_field": field,
        "reason": "clarify numeric percent",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }

    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "ALLOWED"


def test_synonymized_requester_name_resolves():
    g = Gatekeeper('D-ALLOW-2')
    field = "risk_profile.hard_loss_cap_percent"
    ctx = _make_context_with_field(field)
    active_required_fields = {"risk": [field]}
    active_ministers = ["risk"]
    request = {
        "requester": "Minister_of_Risk",
        "requested_field": field,
        "reason": "clarify numeric percent",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }

    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "ALLOWED"
