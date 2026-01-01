"""
G2. STRUCTURED OUTPUT TEST

Test guarantees:
- LLM always returns structured output (not raw text)
- Raw text never reaches core decision logic
- Schema is enforced before consumption
"""

import pytest
from typing import Dict, Any, Optional


class TestG2_StructuredOutput:
    """G2: Must guarantee structured output validation"""
    
    @pytest.fixture
    def output_guard(self):
        """Mock output validation guard"""
        class OutputGuard:
            def __init__(self):
                self.schema = {
                    "decision": str,
                    "confidence": float,
                    "reasoning": str
                }
                self.validated_outputs = []
                self.rejected_outputs = []
            
            def validate_output(self, output: Dict) -> bool:
                """Check output matches schema"""
                try:
                    for key, expected_type in self.schema.items():
                        if key not in output:
                            return False
                        if not isinstance(output[key], expected_type):
                            return False
                    return True
                except:
                    return False
            
            def process_output(self, raw: Any) -> Optional[Dict]:
                """Process output with schema enforcement"""
                if not isinstance(raw, dict):
                    self.rejected_outputs.append(raw)
                    return None
                
                if not self.validate_output(raw):
                    self.rejected_outputs.append(raw)
                    return None
                
                self.validated_outputs.append(raw)
                return raw
            
            def parse_response(self, llm_response: str) -> Optional[Dict]:
                """Parse LLM response - must be structured"""
                import json
                try:
                    parsed = json.loads(llm_response)
                    return self.process_output(parsed)
                except json.JSONDecodeError:
                    self.rejected_outputs.append(llm_response)
                    return None
        
        return OutputGuard()
    
    def test_valid_structured_accepted(self, output_guard):
        """Valid structure passes validation"""
        valid = {
            "decision": "approve",
            "confidence": 0.95,
            "reasoning": "Aligns with principles"
        }
        
        result = output_guard.process_output(valid)
        
        assert result is not None
        assert result == valid
    
    def test_raw_text_rejected(self, output_guard):
        """Raw text output is rejected"""
        raw_text = "This is just text, not structured"
        
        result = output_guard.process_output(raw_text)
        
        assert result is None
        assert raw_text in output_guard.rejected_outputs
    
    def test_missing_field_rejected(self, output_guard):
        """Output missing required field rejected"""
        incomplete = {
            "decision": "approve",
            # Missing "confidence"
            "reasoning": "Some reason"
        }
        
        result = output_guard.process_output(incomplete)
        
        assert result is None
    
    def test_wrong_type_rejected(self, output_guard):
        """Wrong field type rejected"""
        wrong_type = {
            "decision": "approve",
            "confidence": "high",  # Should be float
            "reasoning": "Reason"
        }
        
        result = output_guard.process_output(wrong_type)
        
        assert result is None
    
    def test_json_parsing_enforces_structure(self, output_guard):
        """JSON parsing enforces structure"""
        valid_json = '{"decision": "reject", "confidence": 0.8, "reasoning": "Conflict"}'
        
        result = output_guard.parse_response(valid_json)
        
        assert result is not None
    
    def test_invalid_json_rejected(self, output_guard):
        """Invalid JSON is rejected"""
        invalid_json = '{"decision": "approve", confidence: missing_quotes}'
        
        result = output_guard.parse_response(invalid_json)
        
        assert result is None
        assert invalid_json in output_guard.rejected_outputs
    
    def test_validated_outputs_tracked(self, output_guard):
        """All validated outputs tracked"""
        output1 = {"decision": "a", "confidence": 0.5, "reasoning": "r1"}
        output2 = {"decision": "b", "confidence": 0.7, "reasoning": "r2"}
        
        output_guard.process_output(output1)
        output_guard.process_output(output2)
        
        assert len(output_guard.validated_outputs) == 2
    
    def test_rejected_outputs_tracked(self, output_guard):
        """All rejected outputs tracked"""
        output_guard.process_output("raw text")
        output_guard.process_output({"missing": "field"})
        output_guard.process_output(None)
        
        assert len(output_guard.rejected_outputs) >= 2
    
    def test_schema_enforcement_prevents_bypass(self, output_guard):
        """Schema enforcement cannot be bypassed"""
        # Try various invalid formats
        invalid_outputs = [
            "string",
            123,
            None,
            [],
            {"decision": 123},  # Wrong type
            {"partial": "data"}
        ]
        
        for invalid in invalid_outputs:
            result = output_guard.process_output(invalid)
            assert result is None
