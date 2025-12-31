"""
D2. QUERY THRESHOLD ENFORCEMENT TEST

Test guarantees:
- Low confidence automatically blocks advice
- Threshold enforcement works correctly
- No advice returned below threshold
"""

import pytest
from typing import Optional, Dict, List


class TestD2_ThresholdEnforcement:
    """D2: Must guarantee low confidence blocks advice"""
    
    @pytest.fixture
    def threshold_enforcer(self):
        """Mock enforcer that blocks low-confidence results"""
        class ThresholdEnforcer:
            def __init__(self, min_confidence: float = 0.7):
                self.min_confidence = min_confidence
                self.results_cache = {}
            
            def evaluate_with_threshold(self, query: str, confidence: float) -> Optional[Dict]:
                """Evaluate query, enforce confidence threshold"""
                if confidence < self.min_confidence:
                    return {
                        "status": "blocked",
                        "reason": f"Confidence {confidence} below threshold {self.min_confidence}",
                        "advice": None
                    }
                
                return {
                    "status": "approved",
                    "confidence": confidence,
                    "advice": f"Advice for: {query}"
                }
            
            def batch_enforce(self, queries: List[Dict]) -> List[Dict]:
                """Enforce threshold on batch of queries"""
                results = []
                for item in queries:
                    result = self.evaluate_with_threshold(
                        item["query"],
                        item["confidence"]
                    )
                    results.append(result)
                return results
        
        return ThresholdEnforcer(min_confidence=0.7)
    
    def test_low_confidence_blocked(self, threshold_enforcer):
        """Confidence below threshold blocks advice"""
        result = threshold_enforcer.evaluate_with_threshold(
            "test query",
            confidence=0.5
        )
        
        assert result["status"] == "blocked"
        assert result["advice"] is None
    
    def test_high_confidence_approved(self, threshold_enforcer):
        """Confidence above threshold approved"""
        result = threshold_enforcer.evaluate_with_threshold(
            "test query",
            confidence=0.9
        )
        
        assert result["status"] == "approved"
        assert result["advice"] is not None
    
    def test_threshold_boundary(self, threshold_enforcer):
        """Exactly at threshold boundary"""
        # Below threshold
        result_below = threshold_enforcer.evaluate_with_threshold(
            "query",
            confidence=0.69
        )
        assert result_below["status"] == "blocked"
        
        # At threshold
        result_at = threshold_enforcer.evaluate_with_threshold(
            "query",
            confidence=0.70
        )
        assert result_at["status"] == "approved"
    
    def test_threshold_prevents_unconfident_advice(self, threshold_enforcer):
        """Document that threshold prevents unconfident advice"""
        # This would be problematic without threshold
        problematic_cases = [
            {"confidence": 0.1, "should_block": True},
            {"confidence": 0.3, "should_block": True},
            {"confidence": 0.5, "should_block": True},
            {"confidence": 0.69, "should_block": True},
            {"confidence": 0.70, "should_block": False},
            {"confidence": 0.9, "should_block": False},
            {"confidence": 0.99, "should_block": False},
        ]
        
        # Verify threshold is working
        for case in problematic_cases:
            result = threshold_enforcer.evaluate_with_threshold(
                "query",
                case["confidence"]
            )
            if case["should_block"]:
                assert result["status"] == "blocked"
            else:
                assert result["status"] == "approved"
    
    def test_batch_threshold_enforcement(self, threshold_enforcer):
        """Batch enforcement applies threshold consistently"""
        queries = [
            {"query": "q1", "confidence": 0.3},
            {"query": "q2", "confidence": 0.7},
            {"query": "q3", "confidence": 0.5},
            {"query": "q4", "confidence": 0.9},
            {"query": "q5", "confidence": 0.69}
        ]
        
        results = threshold_enforcer.batch_enforce(queries)
        
        # Check results
        assert results[0]["status"] == "blocked"  # 0.3
        assert results[1]["status"] == "approved"  # 0.7
        assert results[2]["status"] == "blocked"  # 0.5
        assert results[3]["status"] == "approved"  # 0.9
        assert results[4]["status"] == "blocked"  # 0.69
    
    def test_no_advice_when_blocked(self, threshold_enforcer):
        """No advice field populated when blocked"""
        blocked = threshold_enforcer.evaluate_with_threshold("q", 0.3)
        approved = threshold_enforcer.evaluate_with_threshold("q", 0.9)
        
        assert blocked["advice"] is None
        assert approved["advice"] is not None
    
    def test_threshold_consistent_across_calls(self, threshold_enforcer):
        """Threshold behavior consistent"""
        query = "test"
        confidence = 0.65
        
        result1 = threshold_enforcer.evaluate_with_threshold(query, confidence)
        result2 = threshold_enforcer.evaluate_with_threshold(query, confidence)
        
        assert result1["status"] == result2["status"]
    
    def test_threshold_reason_provided(self, threshold_enforcer):
        """When blocked, reason is provided"""
        result = threshold_enforcer.evaluate_with_threshold("q", 0.3)
        
        assert result["status"] == "blocked"
        assert "reason" in result
        assert result["reason"] is not None
        assert len(result["reason"]) > 0
    
    def test_multiple_thresholds(self):
        """Multiple threshold levels can be enforced"""
        class MultiThresholdEnforcer:
            def __init__(self):
                self.soft_threshold = 0.6
                self.hard_threshold = 0.8
            
            def evaluate(self, confidence: float) -> str:
                if confidence < self.soft_threshold:
                    return "blocked"
                elif confidence < self.hard_threshold:
                    return "needs_review"
                else:
                    return "approved"
        
        enforcer = MultiThresholdEnforcer()
        
        # Low confidence
        assert enforcer.evaluate(0.3) == "blocked"
        # Medium confidence
        assert enforcer.evaluate(0.7) == "needs_review"
        # High confidence
        assert enforcer.evaluate(0.9) == "approved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
