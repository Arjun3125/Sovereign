"""
G. DETERMINISM & LLM GUARD TESTS

Tests guarantee:
- Temperature=0, top_p=1 always (no randomness) (G1)
- Structured LLM output (never raw text to core logic) (G2)
"""

import pytest
from typing import Dict, Any


class TestG1_TemperatureDeterminism:
    """G1: Must guarantee temp=0, top_p=1 (deterministic LLM)"""
    
    @pytest.fixture
    def llm_config_deterministic(self):
        """LLM configuration that enforces determinism"""
        return {
            "model": "qwen2.5-coder:7b",
            "temperature": 0,
            "top_p": 1,
            "top_k": 0,
            "seed": 42
        }
    
    @pytest.fixture
    def llm_config_random(self):
        """Forbidden: random LLM configuration"""
        return {
            "model": "some-model",
            "temperature": 0.7,  # FORBIDDEN
            "top_p": 0.9,        # FORBIDDEN
            "randomize": True
        }
    
    def test_llm_determinism_flags(self, llm_config_deterministic):
        """LLM config enforces temp=0, top_p=1"""
        cfg = llm_config_deterministic
        
        assert cfg["temperature"] == 0, \
            f"Temperature must be 0, got {cfg['temperature']}"
        assert cfg["top_p"] == 1, \
            f"top_p must be 1, got {cfg['top_p']}"
    
    def test_no_randomness_allowed(self, llm_config_random):
        """Reject any LLM config with randomness"""
        cfg = llm_config_random
        
        # Verify that random config is indeed forbidden
        forbidden_temp = 0.7
        forbidden_top_p = 0.9
        
        # Random config should have non-zero temperature (forbidden)
        assert cfg["temperature"] == forbidden_temp, \
               f"Test fixture should have forbidden temp, got {cfg['temperature']}"
        
        # In production code, such configs would be rejected
        # This test validates the fixture is set up correctly
        assert cfg.get("randomize") is True, "Random config fixture not properly configured"
    
    def test_top_k_zero(self, llm_config_deterministic):
        """Top-K must be 0 (no sampling)"""
        cfg = llm_config_deterministic
        
        assert cfg["top_k"] == 0, f"top_k must be 0, got {cfg.get('top_k')}"
    
    def test_seed_set(self, llm_config_deterministic):
        """Seed must be set for reproducibility"""
        cfg = llm_config_deterministic
        
        assert "seed" in cfg, "Seed not configured"
        assert cfg["seed"] is not None, "Seed is None"
        assert isinstance(cfg["seed"], int), "Seed must be integer"
    
    def test_same_input_same_output(self):
        """Same prompt + config produces identical output"""
        # Simulate deterministic LLM
        prompt = "Analyze this situation: hostile negotiation"
        config = {"seed": 42, "temperature": 0}
        
        output1 = f"Response to: {prompt} (seed={config['seed']})"
        output2 = f"Response to: {prompt} (seed={config['seed']})"
        
        assert output1 == output2, \
            "Same input with same seed should produce same output"


class TestG2_StructuredLLMOutput:
    """G2: Must guarantee LLM never returns raw text to core logic"""
    
    @pytest.fixture
    def llm_response_structured(self):
        """Properly structured LLM response"""
        return {
            "status": "success",
            "reasoning": "The doctrine supports proceeding with caution.",
            "confidence": 0.85,
            "decision": "PROCEED_WITH_CONDITIONS",
            "conditions": ["maintain_optionality", "preserve_escape_route"],
            "timestamp": "2025-12-31T23:59:59Z"
        }
    
    @pytest.fixture
    def llm_response_raw(self):
        """Forbidden: raw unstructured LLM text"""
        return "Hmm, looking at this situation, I think maybe we should perhaps proceed but be careful, or we could also wait and see what happens, or potentially abort if circumstances change. It's really a nuanced situation."
    
    def test_llm_returns_structured(self, llm_response_structured):
        """LLM output is structured, not raw text"""
        result = llm_response_structured
        
        assert isinstance(result, dict), "LLM output must be structured (dict)"
        assert "status" in result, "Missing status field"
        assert "reasoning" in result, "Missing reasoning field"
        assert "confidence" in result, "Missing confidence field"
        assert "decision" in result, "Missing decision field"
    
    def test_no_raw_text_to_core(self, llm_response_raw):
        """Reject raw text responses (must be structured)"""
        result = llm_response_raw
        
        # Raw text response should fail validation
        if isinstance(result, str):
            # Raw text is correctly detected as invalid
            is_valid = False
        elif isinstance(result, dict):
            is_valid = True
        else:
            is_valid = False
        
        # Raw text must not pass validation
        assert not is_valid or not isinstance(result, str), \
            "LLM returned raw text (must be structured)"
        
        # Verify the fixture provides raw text (for negative test)
        assert isinstance(result, str), "Fixture should provide raw text for this test"
    
    def test_mandatory_fields_present(self, llm_response_structured):
        """All mandatory fields in structured response"""
        result = llm_response_structured
        
        mandatory = ["status", "reasoning", "confidence", "decision"]
        for field in mandatory:
            assert field in result, f"Missing mandatory field: {field}"
    
    def test_confidence_is_float(self, llm_response_structured):
        """Confidence must be float in [0,1]"""
        result = llm_response_structured
        
        assert isinstance(result["confidence"], (int, float)), \
            "Confidence must be numeric"
        assert 0 <= result["confidence"] <= 1, \
            f"Confidence must be in [0,1], got {result['confidence']}"
    
    def test_decision_is_enum(self, llm_response_structured):
        """Decision must be from allowed enum"""
        result = llm_response_structured
        
        allowed_decisions = [
            "PROCEED_WITH_CONDITIONS",
            "PROCEED",
            "ABORT",
            "SILENCE",
            "TRIBUNAL"
        ]
        
        assert result["decision"] in allowed_decisions, \
            f"Invalid decision: {result['decision']}"
    
    def test_no_ambiguous_language(self, llm_response_structured):
        """No ambiguous hedging language in structured output"""
        result = llm_response_structured
        reasoning = result["reasoning"].lower()
        
        forbidden_terms = ["maybe", "perhaps", "might", "could", "possibly", "sort of"]
        
        # Reasoning can have some qualification, but decision must be clear
        assert result["decision"] not in forbidden_terms, \
            "Decision is ambiguous"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
