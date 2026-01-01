import json
import pytest

from cold_strategist.phase1.phase1_prompt import EXAMPLES, validate_response
from cold_strategist.phase1.schema import Phase1Response


def test_all_examples_validate_and_conform():
    """All canonical examples must parse and meet schema constraints."""
    assert isinstance(EXAMPLES, list) and len(EXAMPLES) > 0

    for raw in EXAMPLES:
        # validate_response will raise on parse/validation errors
        resp = validate_response(raw)
        assert isinstance(resp, Phase1Response)

        # Basic semantic checks
        assert resp.status in ("OK", "NEEDS_CONTEXT", "ERROR")
        assert isinstance(resp.reasoning, str) and len(resp.reasoning) > 0
        assert 0.0 <= resp.confidence <= 1.0

        # Decision must include an action string
        assert hasattr(resp.decision, "action")
        assert isinstance(resp.decision.action, str)
        assert len(resp.decision.action) >= 0

        # Actions, if present, must have a type
        if resp.actions:
            for a in resp.actions:
                assert hasattr(a, "type")
                assert isinstance(a.type, str) and len(a.type) > 0
