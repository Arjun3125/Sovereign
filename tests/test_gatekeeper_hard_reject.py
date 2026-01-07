import time
import pytest

pytestmark = pytest.mark.policy

from cold_strategist.core.gatekeeper import Gatekeeper


def _make_context():
    return {"identity": {}, "risk_profile": {}}


def test_field_not_in_schema_rejected():
    g = Gatekeeper('D-REJ-1')
    ctx = _make_context()
    active_required_fields = {"risk": ["risk_profile.hard_loss_cap_percent"]}
    active_ministers = ["risk"]
    request = {
        "requester": "risk",
        "requested_field": "nonexistent.field",
        "reason": "need this",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }
    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "REJECTED"
    assert res["reason"] == "FIELD_INVALID"


def test_field_not_required_by_active_minister_rejected():
    g = Gatekeeper('D-REJ-2')
    field = "risk_profile.hard_loss_cap_percent"
    ctx = {"risk_profile": {"hard_loss_cap_percent": {}}}
    active_required_fields = {"risk": [field]}
    active_ministers = ["psychology"]
    request = {
        "requester": "psychology",
        "requested_field": field,
        "reason": "clarify",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }
    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "REJECTED"
    assert res["reason"] == "FIELD_NOT_REQUIRED_BY_ACTIVE_MINISTER"


def test_open_ended_question_rejected():
    g = Gatekeeper('D-REJ-3')
    field = "risk_profile.hard_loss_cap_percent"
    ctx = {"risk_profile": {"hard_loss_cap_percent": {}}}
    active_required_fields = {"risk": [field]}
    active_ministers = ["risk"]
    request = {
        "requester": "risk",
        "requested_field": field,
        "reason": "why did this happen?",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }
    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "REJECTED"
    assert res["reason"] == "OPEN_ENDED_OR_OUT_OF_SCOPE"


def test_redundant_question_within_n_turns_rejected():
    g = Gatekeeper('D-REJ-4')
    g.question_history.append({"requested_field": "risk_profile.hard_loss_cap_percent", "status": "REJECTED"})
    field = "risk_profile.hard_loss_cap_percent"
    ctx = {"risk_profile": {"hard_loss_cap_percent": {}}}
    active_required_fields = {"risk": [field]}
    active_ministers = ["risk"]
    request = {
        "requester": "risk",
        "requested_field": field,
        "reason": "clarify",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }
    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "REJECTED"
    assert res["reason"] == "PREVIOUSLY_REFUSED"


def test_budget_exhausted_rejected():
    g = Gatekeeper('D-REJ-5')
    # populate history to reach budget
    for _ in range(g.max_questions):
        g.question_history.append({"requested_field": "f", "status": "ALLOWED"})

    field = "risk_profile.hard_loss_cap_percent"
    ctx = {"risk_profile": {"hard_loss_cap_percent": {}}}
    active_required_fields = {"risk": [field]}
    active_ministers = ["risk"]
    request = {
        "requester": "risk",
        "requested_field": field,
        "reason": "clarify",
        "decision_id": g.decision_id,
        "context_snapshot": ctx,
    }
    res = g.can_ask(request, ctx, active_required_fields, active_ministers)
    assert res["status"] == "REJECTED"
    assert res["reason"] == "BUDGET_EXHAUSTED"
