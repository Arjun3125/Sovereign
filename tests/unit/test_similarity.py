"""
L1 Test Suite — Similarity & Core Retrieval Mechanics
Tests fundamental cosine similarity behavior [RULE-1-1, 1-2, 1-3]
"""
import math
import pytest
from tests.conftest import assert_rule, assert_approximately_equal, assert_no_overlap


class TestSimilarity:
    """Test cosine similarity computation."""
    
    def cosine_similarity(self, vec_a: list, vec_b: list) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec_a) != len(vec_b):
            raise ValueError("Vectors must be same length")
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
        norm_b = math.sqrt(sum(b ** 2 for b in vec_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        sim = dot_product / (norm_a * norm_b)
        # Hard clamp for numerical stability — bounds are contractual, not optional
        return max(0.0, min(1.0, float(sim)))
    
    def test_identical_vectors_similarity_one(self):
        """Same input vectors → similarity ≈ 1.0 [RULE-1-3]"""
        vec = [0.5] * 768
        similarity = self.cosine_similarity(vec, vec)
        assert_approximately_equal(
            similarity, 1.0, tolerance=0.001,
            rule_id="RULE-1-3",
            message="Identical vectors must have similarity ≈ 1.0"
        )
    
    def test_deterministic_similarity(self):
        """Same input vectors → same similarity score (deterministic) [RULE-1-1]"""
        vec_a = [0.1, 0.2, 0.3] * 256  # 768 total
        vec_b = [0.15, 0.25, 0.35] * 256
        
        # Compute twice
        sim1 = self.cosine_similarity(vec_a, vec_b)
        sim2 = self.cosine_similarity(vec_a, vec_b)
        
        assert_rule(
            sim1 == sim2,
            "RULE-1-1",
            f"Similarity computation must be deterministic. Got {sim1} then {sim2}"
        )
    
    def test_orthogonal_vectors_near_zero(self):
        """Orthogonal vectors → similarity near 0 [RULE-1-2]"""
        vec_a = [1.0] * 384 + [0.0] * 384
        vec_b = [0.0] * 384 + [1.0] * 384
        
        similarity = self.cosine_similarity(vec_a, vec_b)
        assert_approximately_equal(
            similarity, 0.0, tolerance=0.001,
            rule_id="RULE-1-2",
            message="Orthogonal vectors must have similarity ≈ 0"
        )
    
    def test_similarity_range(self):
        """Similarity always in [0, 1] range"""
        test_cases = [
            ([1, 0, 0], [1, 0, 0]),  # identical
            ([1, 0, 0], [0, 1, 0]),  # orthogonal
            ([1, 1, 1], [2, 2, 2]),  # proportional
            ([0.1, 0.2, 0.3], [0.4, 0.5, 0.6]),  # random
        ]
        
        for vec_a, vec_b in test_cases:
            similarity = self.cosine_similarity(vec_a, vec_b)
            assert_rule(
                0.0 <= similarity <= 1.0,
                "RULE-1-1",
                f"Similarity must be in [0, 1], got {similarity}"
            )
    
    def test_symmetry(self):
        """Similarity(A, B) == Similarity(B, A)"""
        vec_a = [0.1, 0.2, 0.3, 0.4, 0.5]
        vec_b = [0.5, 0.4, 0.3, 0.2, 0.1]
        
        sim_ab = self.cosine_similarity(vec_a, vec_b)
        sim_ba = self.cosine_similarity(vec_b, vec_a)
        
        assert_rule(
            abs(sim_ab - sim_ba) < 1e-10,
            "RULE-1-1",
            f"Similarity must be symmetric. sim(A,B)={sim_ab}, sim(B,A)={sim_ba}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
