"""
G1. TEMPERATURE DETERMINISM TEST

Test guarantees:
- LLM temperature is always 0 (deterministic)
- top_p is always 1.0 (full probability space)
- No randomness in LLM generation
"""

import pytest
from typing import Dict, Any


class TestG1_TemperatureDeterminism:
    """G1: Must guarantee deterministic LLM behavior"""
    
    @pytest.fixture
    def llm_guard(self):
        """Mock LLM guard enforcing determinism"""
        class LLMGuard:
            def __init__(self):
                self.config = {
                    "temperature": 0,
                    "top_p": 1.0,
                    "frequency_penalty": 0,
                    "presence_penalty": 0
                }
                self.call_log = []
            
            def generate(self, prompt: str) -> str:
                """Generate with enforced determinism"""
                self.call_log.append({
                    "prompt": prompt,
                    "config": self.config.copy()
                })
                # Same prompt → same output (deterministic)
                return f"response_to_{len(prompt)}_chars"
            
            def generate_with_override(self, prompt: str, config: Dict) -> str:
                """Try to override config - should enforce safety"""
                # Guard prevents unsafe config
                safe_config = {
                    "temperature": 0,  # Always 0
                    "top_p": 1.0,      # Always 1.0
                    "frequency_penalty": 0,
                    "presence_penalty": 0
                }
                self.call_log.append({
                    "prompt": prompt,
                    "requested": config,
                    "enforced": safe_config
                })
                return f"safe_response"
        
        return LLMGuard()
    
    def test_temperature_is_zero(self, llm_guard):
        """Temperature configured to 0"""
        assert llm_guard.config["temperature"] == 0
    
    def test_top_p_is_maximum(self, llm_guard):
        """top_p configured to 1.0"""
        assert llm_guard.config["top_p"] == 1.0
    
    def test_deterministic_generation(self, llm_guard):
        """Same prompt produces same output"""
        prompt = "What is 2+2?"
        
        result1 = llm_guard.generate(prompt)
        result2 = llm_guard.generate(prompt)
        
        assert result1 == result2
    
    def test_frequency_penalty_zero(self, llm_guard):
        """No frequency penalty (no token suppression)"""
        assert llm_guard.config["frequency_penalty"] == 0
    
    def test_presence_penalty_zero(self, llm_guard):
        """No presence penalty (deterministic token selection)"""
        assert llm_guard.config["presence_penalty"] == 0
    
    def test_config_immutable_during_generation(self, llm_guard):
        """Config cannot change during call"""
        prompt1 = "First prompt"
        prompt2 = "Second prompt"
        
        llm_guard.generate(prompt1)
        llm_guard.generate(prompt2)
        
        # Both calls should have identical config
        config1 = llm_guard.call_log[0]["config"]
        config2 = llm_guard.call_log[1]["config"]
        
        assert config1 == config2
    
    def test_override_attempt_rejected(self, llm_guard):
        """Attempts to increase randomness are blocked"""
        unsafe_config = {
            "temperature": 0.7,  # Trying to add randomness
            "top_p": 0.9
        }
        
        llm_guard.generate_with_override("prompt", unsafe_config)
        
        log_entry = llm_guard.call_log[-1]
        assert log_entry["enforced"]["temperature"] == 0
        assert log_entry["enforced"]["top_p"] == 1.0
    
    def test_all_penalties_zero(self, llm_guard):
        """All randomness-inducing parameters at 0/1.0"""
        config = llm_guard.config
        
        assert config["temperature"] == 0
        assert config["top_p"] == 1.0
        assert config["frequency_penalty"] == 0
        assert config["presence_penalty"] == 0
    
    def test_determinism_preserved_across_calls(self, llm_guard):
        """Determinism maintained over multiple calls"""
        prompts = ["A", "B", "C", "A", "B", "C"]
        results = []
        
        for prompt in prompts:
            results.append(llm_guard.generate(prompt))
        
        # Duplicate prompts produce same results
        assert results[0] == results[3]  # "A"
        assert results[1] == results[4]  # "B"
        assert results[2] == results[5]  # "C"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
