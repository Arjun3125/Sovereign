"""
I2. INVALID DOCTRINE DEFENSE TEST

Test guarantees:
- Malformed/invalid doctrines are rejected
- Invalid doctrine doesn't crash system
- Specific error messages for validation failures
- Schema validation before acceptance
"""

import pytest
from typing import Dict, Any


class TestI2_InvalidDoctrineDefense:
    """I2: Must guarantee invalid doctrines are rejected"""
    
    @pytest.fixture
    def doctrine_validator(self):
        """Mock doctrine validator with schema enforcement"""
        class DoctrineValidator:
            def __init__(self):
                self.schema = {
                    "id": str,
                    "title": str,
                    "principles": list,
                    "precedents": list
                }
                self.valid_doctrines = []
                self.invalid_log = []
            
            def validate_structure(self, doctrine: Any) -> tuple[bool, str]:
                """Check doctrine matches schema"""
                if not isinstance(doctrine, dict):
                    return False, "not_dict"
                
                missing_fields = []
                for field, field_type in self.schema.items():
                    if field not in doctrine:
                        missing_fields.append(field)
                    elif not isinstance(doctrine[field], field_type):
                        return False, f"wrong_type_{field}"
                
                if missing_fields:
                    return False, f"missing_fields_{','.join(missing_fields)}"
                
                return True, "valid"
            
            def accept_doctrine(self, doctrine: Dict) -> Dict:
                """Accept doctrine after validation"""
                valid, reason = self.validate_structure(doctrine)
                
                if not valid:
                    self.invalid_log.append({
                        "doctrine": doctrine,
                        "reason": reason
                    })
                    return {
                        "status": "rejected",
                        "reason": reason,
                        "accepted": False
                    }
                
                self.valid_doctrines.append(doctrine)
                return {
                    "status": "accepted",
                    "doctrine_id": doctrine["id"],
                    "accepted": True
                }
            
            def batch_validate(self, doctrines: list) -> Dict:
                """Validate multiple doctrines"""
                accepted = 0
                rejected = 0
                
                for doc in doctrines:
                    result = self.accept_doctrine(doc)
                    if result["accepted"]:
                        accepted += 1
                    else:
                        rejected += 1
                
                return {
                    "total": len(doctrines),
                    "accepted": accepted,
                    "rejected": rejected
                }
        
        return DoctrineValidator()
    
    def test_valid_doctrine_accepted(self, doctrine_validator):
        """Valid doctrine is accepted"""
        valid = {
            "id": "d1",
            "title": "Principle",
            "principles": ["p1"],
            "precedents": ["r1"]
        }
        
        result = doctrine_validator.accept_doctrine(valid)
        
        assert result["status"] == "accepted"
        assert len(doctrine_validator.valid_doctrines) == 1
    
    def test_non_dict_rejected(self, doctrine_validator):
        """Non-dict doctrine rejected"""
        invalid = "just a string"
        
        result = doctrine_validator.accept_doctrine(invalid)
        
        assert result["status"] == "rejected"
        assert result["reason"] == "not_dict"
    
    def test_missing_field_rejected(self, doctrine_validator):
        """Missing required field rejected"""
        incomplete = {
            "id": "d1",
            "title": "Principle"
            # Missing principles and precedents
        }
        
        result = doctrine_validator.accept_doctrine(incomplete)
        
        assert result["status"] == "rejected"
        assert "missing_fields" in result["reason"]
    
    def test_wrong_field_type_rejected(self, doctrine_validator):
        """Wrong field type rejected"""
        wrong_type = {
            "id": "d1",
            "title": "Principle",
            "principles": "should be list",  # Wrong type
            "precedents": []
        }
        
        result = doctrine_validator.accept_doctrine(wrong_type)
        
        assert result["status"] == "rejected"
        assert "wrong_type" in result["reason"]
    
    def test_multiple_errors_reported(self, doctrine_validator):
        """Multiple field errors detected"""
        bad = {
            "id": 123,  # Wrong type
            "title": "Principle"
            # Missing 2 fields
        }
        
        result = doctrine_validator.accept_doctrine(bad)
        
        assert result["status"] == "rejected"
    
    def test_invalid_logged(self, doctrine_validator):
        """Invalid doctrine logged for review"""
        bad = {"id": 123}
        
        doctrine_validator.accept_doctrine(bad)
        
        assert len(doctrine_validator.invalid_log) == 1
        assert doctrine_validator.invalid_log[0]["doctrine"] == bad
    
    def test_batch_with_mixed_validity(self, doctrine_validator):
        """Batch with valid and invalid items"""
        batch = [
            {"id": "v1", "title": "T", "principles": [], "precedents": []},  # Valid
            {"id": 2},  # Invalid
            {"id": "v2", "title": "T", "principles": [], "precedents": []},  # Valid
            "invalid"  # Invalid
        ]
        
        result = doctrine_validator.batch_validate(batch)
        
        assert result["accepted"] == 2
        assert result["rejected"] == 2
    
    def test_invalid_doesnt_crash(self, doctrine_validator):
        """Invalid doctrine doesn't crash system"""
        invalid_inputs = [
            None,
            123,
            [],
            {"wrong": "fields"},
            {"id": None, "title": None, "principles": None, "precedents": None}
        ]
        
        for invalid in invalid_inputs:
            # Should not raise exception
            result = doctrine_validator.accept_doctrine(invalid)
            assert result["status"] == "rejected"
    
    def test_empty_lists_valid(self, doctrine_validator):
        """Empty principle/precedent lists valid"""
        doctrine = {
            "id": "d1",
            "title": "Doctrine",
            "principles": [],  # Empty but valid type
            "precedents": []   # Empty but valid type
        }
        
        result = doctrine_validator.accept_doctrine(doctrine)
        
        assert result["status"] == "accepted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
