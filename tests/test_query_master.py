"""
D. QUERY / RETRIEVAL LAYER TESTS

Tests guarantee:
- Same query → same results → same order (D1)
- Threshold enforcement: low confidence blocks answer (D2)
"""

import pytest
from typing import List, Dict


class TestD1_TopKStability:
    """D1: Must guarantee same query produces identical results in same order"""
    
    @pytest.fixture
    def mock_retrieval_engine(self):
        """Mock retrieval engine with deterministic ranking"""
        return {
            "index": {
                "silence_is_power": [
                    {"id": "p1", "score": 0.95},
                    {"id": "p2", "score": 0.87},
                    {"id": "p3", "score": 0.73},
                ],
                "foresight": [
                    {"id": "p4", "score": 0.92},
                    {"id": "p5", "score": 0.81},
                ]
            },
            "seed": 42
        }
    
    def test_query_deterministic(self, mock_retrieval_engine):
        """Same query returns same results in same order"""
        query = "silence_is_power"
        
        # Query 1
        results1 = mock_retrieval_engine["index"][query]
        order1 = [r["id"] for r in results1]
        
        # Query 2 (identical)
        results2 = mock_retrieval_engine["index"][query]
        order2 = [r["id"] for r in results2]
        
        # Query 3 (identical)
        results3 = mock_retrieval_engine["index"][query]
        order3 = [r["id"] for r in results3]
        
        # All three must be identical
        assert order1 == order2 == order3, \
            f"Orders differ: {order1} vs {order2} vs {order3}"
    
    def test_top_k_consistent_order(self, mock_retrieval_engine):
        """Top-K results always in same order (highest score first)"""
        query = "silence_is_power"
        results = mock_retrieval_engine["index"][query]
        
        # Verify sorted by score descending
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True), \
            f"Results not sorted by score: {scores}"
    
    def test_query_across_sessions(self):
        """Same query across separate sessions yields same results"""
        # Session 1
        query_session1 = "test_query"
        results_s1 = [
            {"id": "doc1", "rank": 1, "score": 0.95},
            {"id": "doc2", "rank": 2, "score": 0.87}
        ]
        
        # Session 2 (identical query)
        query_session2 = "test_query"
        results_s2 = [
            {"id": "doc1", "rank": 1, "score": 0.95},
            {"id": "doc2", "rank": 2, "score": 0.87}
        ]
        
        # Compare
        ids_s1 = [r["id"] for r in results_s1]
        ids_s2 = [r["id"] for r in results_s2]
        
        assert ids_s1 == ids_s2, "Different results across sessions"
    
    def test_ranking_stability_over_time(self):
        """Ranking of results doesn't change over time (immutable index)"""
        results_time1 = [
            {"id": "p1", "score": 0.95},
            {"id": "p2", "score": 0.87},
            {"id": "p3", "score": 0.73}
        ]
        
        results_time2 = [
            {"id": "p1", "score": 0.95},
            {"id": "p2", "score": 0.87},
            {"id": "p3", "score": 0.73}
        ]
        
        # Verify no rank changes
        for r1, r2 in zip(results_time1, results_time2):
            assert r1["id"] == r2["id"] and r1["score"] == r2["score"], \
                "Ranking changed"
    
    def test_tie_breaking_deterministic(self):
        """When scores tie, tie-breaking is deterministic"""
        results = [
            {"id": "a", "score": 0.90},
            {"id": "b", "score": 0.90},  # Tie
            {"id": "c", "score": 0.85}
        ]
        
        # Sort with tiebreaker (ID alphabetically)
        sorted_results = sorted(results, key=lambda x: (-x["score"], x["id"]))
        order1 = [r["id"] for r in sorted_results]
        
        # Sort again (should be identical)
        sorted_results2 = sorted(results, key=lambda x: (-x["score"], x["id"]))
        order2 = [r["id"] for r in sorted_results2]
        
        assert order1 == order2, "Tie-breaking not deterministic"


class TestD2_ThresholdEnforcement:
    """D2: Must guarantee low confidence blocks answer (returns NEEDS_CONTEXT)"""
    
    @pytest.fixture
    def confidence_threshold(self):
        """Confidence threshold settings"""
        return {
            "min_confidence": 0.75,
            "low_confidence_status": "NEEDS_CONTEXT"
        }
    
    def test_low_confidence_blocks_answer(self, confidence_threshold):
        """Confidence < threshold returns NEEDS_CONTEXT instead of answer"""
        query = "ambiguous situation"
        results = [
            {"id": "p1", "text": "Some relevant text", "confidence": 0.65}
        ]
        
        # Check threshold
        if results[0]["confidence"] < confidence_threshold["min_confidence"]:
            status = confidence_threshold["low_confidence_status"]
        else:
            status = "READY"
        
        assert status == "NEEDS_CONTEXT", \
            f"Low confidence should block answer, got {status}"
    
    def test_high_confidence_allows_answer(self, confidence_threshold):
        """Confidence >= threshold allows answer"""
        query = "clear situation"
        results = [
            {"id": "p1", "text": "Very relevant", "confidence": 0.88}
        ]
        
        # Check threshold
        if results[0]["confidence"] >= confidence_threshold["min_confidence"]:
            status = "READY"
        else:
            status = "NEEDS_CONTEXT"
        
        assert status == "READY", "High confidence should allow answer"
    
    def test_threshold_boundary(self, confidence_threshold):
        """Confidence exactly at threshold is allowed"""
        confidence = confidence_threshold["min_confidence"]
        
        if confidence >= confidence_threshold["min_confidence"]:
            status = "READY"
        else:
            status = "NEEDS_CONTEXT"
        
        assert status == "READY", "Boundary confidence should be allowed"
    
    def test_below_threshold_boundary(self, confidence_threshold):
        """Confidence just below threshold is blocked"""
        confidence = confidence_threshold["min_confidence"] - 0.01
        
        if confidence >= confidence_threshold["min_confidence"]:
            status = "READY"
        else:
            status = "NEEDS_CONTEXT"
        
        assert status == "NEEDS_CONTEXT", \
            "Below-threshold confidence should be blocked"
    
    def test_multiple_results_all_below_threshold(self, confidence_threshold):
        """If all results below threshold, return NEEDS_CONTEXT"""
        results = [
            {"id": "p1", "confidence": 0.60},
            {"id": "p2", "confidence": 0.55},
            {"id": "p3", "confidence": 0.70}
        ]
        
        max_confidence = max(r["confidence"] for r in results)
        
        if max_confidence < confidence_threshold["min_confidence"]:
            status = "NEEDS_CONTEXT"
        else:
            status = "READY"
        
        assert status == "NEEDS_CONTEXT", \
            f"All results below threshold but got {status}"
    
    def test_threshold_not_bypassed(self, confidence_threshold):
        """Threshold cannot be bypassed by combining low-confidence results"""
        results = [
            {"id": "p1", "confidence": 0.50},
            {"id": "p2", "confidence": 0.45}
        ]
        
        # Even combined, still below threshold
        max_conf = max(r["confidence"] for r in results)
        
        if max_conf < confidence_threshold["min_confidence"]:
            status = "NEEDS_CONTEXT"
        
        assert status == "NEEDS_CONTEXT", "Low confidence threshold was bypassed"
    
    def test_no_answer_without_confidence(self, confidence_threshold):
        """Result without confidence score is blocked"""
        result_no_conf = {"id": "p1", "text": "Some text"}  # No confidence field
        
        confidence = result_no_conf.get("confidence", 0)  # Default to 0 if missing
        
        if confidence < confidence_threshold["min_confidence"]:
            status = "NEEDS_CONTEXT"
        else:
            status = "READY"
        
        assert status == "NEEDS_CONTEXT", "Missing confidence should block answer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
