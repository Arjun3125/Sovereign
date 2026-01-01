import json
import pytest

from cold_strategist.phase1.phase1_prompt import PROMPT, EXAMPLES, validate_response
from cold_strategist.phase1.schema import Phase1Response


def test_prompt_and_examples_present():
    assert isinstance(PROMPT, str) and len(PROMPT) > 0
    assert isinstance(EXAMPLES, list) and len(EXAMPLES) >= 1


def test_validate_response_accepts_valid_example():
    raw = EXAMPLES[0]
    resp = validate_response(raw)
    assert isinstance(resp, Phase1Response)
    assert resp.status == "OK"


def test_validate_response_rejects_raw_text():
    raw = "I think you should proceed but I'm not sure."
    with pytest.raises(ValueError):
        validate_response(raw)


def test_validate_response_missing_field_fails():
    # Remove required field 'status'
    bad = json.dumps({"reasoning": "ok", "confidence": 0.5, "decision": {"action": "none"}})
    with pytest.raises(Exception):
        validate_response(bad)
