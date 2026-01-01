import pytest
from cold_strategist.phase1.schema import Phase1Response, Decision, ActionItem
from cold_strategist.phase3 import Phase3Evaluator, apply_phase3_routing, Phase3Assessment


class TestPhase3Evaluator:
    """Test Phase-3 evaluation logic."""

    def test_phase3_evaluator_error_status(self):
        """Phase-1 ERROR status → REQUEST_MORE_INFO."""
        resp = Phase1Response(
            status="ERROR",
            reasoning="Parsing failed",
            confidence=0.0,
            decision=Decision(action="", parameters={}),
        )
        
        evaluator = Phase3Evaluator()
        assessment = evaluator.evaluate(resp)
        
        assert assessment.phase1_status == "ERROR"
        assert assessment.decision == "REQUEST_MORE_INFO"
        assert assessment.requires_more_context()

    def test_phase3_evaluator_needs_context_status(self):
        """Phase-1 NEEDS_CONTEXT → REQUEST_MORE_INFO with actions."""
        resp = Phase1Response(
            status="NEEDS_CONTEXT",
            reasoning="Location missing; cannot assess urgency",
            confidence=0.0,
            decision=Decision(action="none", parameters={}),
            actions=[ActionItem(type="GATHER_INFO", description="Request location from reporter")],
        )
        
        evaluator = Phase3Evaluator()
        assessment = evaluator.evaluate(resp)
        
        assert assessment.phase1_status == "NEEDS_CONTEXT"
        assert assessment.decision == "REQUEST_MORE_INFO"
        assert assessment.requires_more_context()
        assert assessment.actions is not None

    def test_phase3_evaluator_high_confidence_ok(self):
        """Phase-1 OK + high confidence (>=0.75) → PROCEED with Quick mode."""
        resp = Phase1Response(
            status="OK",
            reasoning="Clear situation with sufficient context.",
            confidence=0.85,
            decision=Decision(action="engage", parameters={"level": "limited"}),
        )
        
        evaluator = Phase3Evaluator()
        assessment = evaluator.evaluate(resp)
        
        assert assessment.phase1_status == "OK"
        assert assessment.decision == "PROCEED"
        assert assessment.recommended_mode == "quick"
        assert assessment.should_proceed_inline()

    def test_phase3_evaluator_medium_confidence_ok(self):
        """Phase-1 OK + medium confidence (0.5-0.75) → ESCALATE to Normal mode."""
        resp = Phase1Response(
            status="OK",
            reasoning="Some clarity but gaps remain.",
            confidence=0.65,
            decision=Decision(action="monitor", parameters={"period": "2h"}),
        )
        
        evaluator = Phase3Evaluator()
        assessment = evaluator.evaluate(resp)
        
        assert assessment.phase1_status == "OK"
        assert assessment.decision == "ESCALATE"
        assert assessment.recommended_mode == "normal"
        assert assessment.should_escalate_to_debate()

    def test_phase3_evaluator_low_confidence_ok(self):
        """Phase-1 OK + low confidence (<0.5) → ESCALATE (conservative)."""
        resp = Phase1Response(
            status="OK",
            reasoning="Indicators point to potential threat but evidence weak.",
            confidence=0.35,
            decision=Decision(action="monitor", parameters={"period": "2h"}),
        )
        
        evaluator = Phase3Evaluator()
        assessment = evaluator.evaluate(resp)
        
        assert assessment.phase1_status == "OK"
        assert assessment.decision == "ESCALATE"
        assert assessment.recommended_mode == "normal"
        assert assessment.should_escalate_to_debate()

    def test_phase3_evaluator_boundary_confidence(self):
        """Test boundary at 0.75 and 0.5 confidence thresholds."""
        evaluator = Phase3Evaluator()
        
        # Exactly 0.75: should PROCEED
        resp_75 = Phase1Response(
            status="OK",
            reasoning="Test",
            confidence=0.75,
            decision=Decision(action="test"),
        )
        assess_75 = evaluator.evaluate(resp_75)
        assert assess_75.decision == "PROCEED"
        
        # Just below 0.75: should ESCALATE
        resp_74 = Phase1Response(
            status="OK",
            reasoning="Test",
            confidence=0.74,
            decision=Decision(action="test"),
        )
        assess_74 = evaluator.evaluate(resp_74)
        assert assess_74.decision == "ESCALATE"


class TestApplyPhase3Routing:
    """Test Phase-3 routing wrapper function."""

    def test_apply_phase3_routing_with_custom_evaluator(self):
        """Test routing with custom evaluator."""
        resp = Phase1Response(
            status="OK",
            reasoning="Clear",
            confidence=0.8,
            decision=Decision(action="proceed"),
        )
        
        evaluator = Phase3Evaluator()
        assessment, mode = apply_phase3_routing(resp, evaluator)
        
        assert isinstance(assessment, Phase3Assessment)
        assert mode == "quick"

    def test_apply_phase3_routing_without_evaluator(self):
        """Test routing with default evaluator."""
        resp = Phase1Response(
            status="OK",
            reasoning="Escalation needed",
            confidence=0.6,
            decision=Decision(action="escalate"),
        )
        
        assessment, mode = apply_phase3_routing(resp)
        
        assert mode == "normal"

    def test_apply_phase3_routing_needs_context(self):
        """Test routing when more context is needed."""
        resp = Phase1Response(
            status="NEEDS_CONTEXT",
            reasoning="Not enough info",
            confidence=0.0,
            decision=Decision(action="none"),
        )
        
        assessment, mode = apply_phase3_routing(resp)
        
        assert mode is None  # No mode override when requesting more info
        assert assessment.requires_more_context()


class TestOrchestratorPhase3Integration:
    """Test Orchestrator with Phase-1 → Phase-3 pipeline."""

    def test_orchestrator_assess_and_route_pipeline_logic(self):
        """Test Phase-1 → Phase-3 routing pipeline logic directly."""
        # Create a Phase-1 response
        resp = Phase1Response(
            status="OK",
            reasoning="Sufficient context provided.",
            confidence=0.8,
            decision=Decision(action="proceed", parameters={"mode": "quick"}),
        )
        
        # Apply Phase-3 evaluation
        phase3, mode = apply_phase3_routing(resp)
        
        # Verify pipeline consistency
        assert isinstance(phase3, Phase3Assessment)
        assert phase3.phase1_status == "OK"
        assert phase3.phase1_confidence == 0.8
        assert phase3.should_proceed_inline()
        assert mode == "quick"

    def test_orchestrator_phase3_confidence_routing(self):
        """Test Phase-3 routes based on Phase-1 confidence levels."""
        # Test case 1: High confidence → Quick
        high_conf = Phase1Response(
            status="OK",
            reasoning="Clear",
            confidence=0.82,
            decision=Decision(action="proceed"),
        )
        assess_high, mode_high = apply_phase3_routing(high_conf)
        assert mode_high == "quick"
        
        # Test case 2: Medium confidence → Normal
        med_conf = Phase1Response(
            status="OK",
            reasoning="Some gaps",
            confidence=0.65,
            decision=Decision(action="escalate"),
        )
        assess_med, mode_med = apply_phase3_routing(med_conf)
        assert mode_med == "normal"
        
        # Test case 3: Low confidence → Normal (conservative)
        low_conf = Phase1Response(
            status="OK",
            reasoning="Weak evidence",
            confidence=0.30,
            decision=Decision(action="escalate"),
        )
        assess_low, mode_low = apply_phase3_routing(low_conf)
        assert mode_low == "normal"

    def test_phase1_phase3_integration_end_to_end(self):
        """End-to-end test: Phase-1 → Phase-3 → Mode routing.
        
        This requires OLLAMA setup but tests full pipeline integration.
        """
        import os
        if not os.getenv("OLLAMA_URL") or not os.getenv("OLLAMA_MODEL"):
            pytest.skip("OLLAMA not configured")

        from cold_strategist.phase1.llm_client import call_llm
        from cold_strategist.phase1.phase1_prompt import PROMPT, validate_response
        from cold_strategist.phase3 import apply_phase3_routing
        
        # Step 1: Phase-1 assessment
        situation = "Escalation in northern sector with unclear actors."
        full_prompt = PROMPT + "\n\nSITUATION:\n" + situation + "\n\nRespond with a single JSON object."
        
        try:
            raw = call_llm(full_prompt)
            phase1_resp = validate_response(raw)
        except Exception as e:
            # LLM may return malformed response; skip this test
            pytest.skip(f"LLM returned invalid response: {e}")
        
        # Step 2: Phase-3 routing (should not raise)
        phase3_assessment, mode = apply_phase3_routing(phase1_resp)
        
        # Step 3: Verify consistency
        assert isinstance(phase1_resp, Phase1Response)
        assert isinstance(phase3_assessment, Phase3Assessment)
        assert phase3_assessment.phase1_status == phase1_resp.status
        assert phase3_assessment.phase1_confidence == phase1_resp.confidence
        
        # Mode should be routable
        if phase3_assessment.decision in ("PROCEED", "ESCALATE"):
            assert mode in ("quick", "normal", "war")
        else:
            assert mode is None
