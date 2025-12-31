"""
L1 Test Suite — MinisterRetriever
Tests domain isolation, confidence weighting, graceful failure [RULE-1-4, 1-5]
"""
import pytest
from tests.conftest import assert_rule, assert_no_overlap


class MockMinisterRetriever:
    """Mock retriever for testing (real one imported in integration tests)."""
    
    def __init__(self, domain: str, principles: list):
        """
        Args:
            domain: Domain filter (e.g., "psychology", "power")
            principles: List of principle dicts with domain_fit, embedding, etc.
        """
        self.domain = domain
        self.principles = principles
    
    def retrieve(self, query: str, k: int = 3) -> list:
        """
        Retrieve top-k principles matching domain.
        
        Returns list of dicts with:
        - principle: text
        - similarity: float (mock: random)
        - confidence_weight: float
        - score: similarity × confidence_weight
        - domain_fit: list of domains
        """
        # Filter by domain
        filtered = [
            p for p in self.principles 
            if self.domain in p.get("domain_fit", [])
        ]
        
        # Mock scoring (not testing similarity computation here, just filtering)
        scored = [
            {
                "principle": p["principle"],
                "similarity": 0.5,  # Mock
                "confidence_weight": p.get("confidence_weight", 0.7),
                "score": 0.5 * p.get("confidence_weight", 0.7),
                "domain_fit": p.get("domain_fit", []),
                "source": p.get("source", {}),
            }
            for p in filtered
        ]
        
        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]


class TestMinisterRetriever:
    """Test retriever behavior."""
    
    def test_psychology_minister_respects_domain_filter(self, sample_principles):
        """Retriever respects domain filter. [RULE-1-4]"""
        retriever = MockMinisterRetriever("psychology", sample_principles)
        results = retriever.retrieve("any query", k=5)
        
        # All results must have "psychology" in domain_fit
        for result in results:
            assert_rule(
                "psychology" in result["domain_fit"],
                "RULE-1-4",
                f"Psychology retriever returned principle without psychology domain: {result['principle']}"
            )
    
    def test_psychology_minister_never_returns_power_only(self, sample_principles):
        """Psychology minister NEVER returns power-only principles. [RULE-1-5]"""
        retriever = MockMinisterRetriever("psychology", sample_principles)
        results = retriever.retrieve("query", k=10)
        
        # Collect all domain_fit lists
        psychology_domains = [r["domain_fit"] for r in results]
        power_only = [
            d for d in psychology_domains 
            if d == ["power"]  # Power-only principles
        ]
        
        assert_rule(
            len(power_only) == 0,
            "RULE-1-5",
            f"Psychology minister returned {len(power_only)} power-only principles. Violation of critical boundary."
        )
    
    def test_power_minister_respects_domain_filter(self, sample_principles):
        """Power minister returns only power-domain principles. [RULE-1-4]"""
        retriever = MockMinisterRetriever("power", sample_principles)
        results = retriever.retrieve("query", k=5)
        
        for result in results:
            assert_rule(
                "power" in result["domain_fit"],
                "RULE-1-4",
                f"Power retriever returned principle without power domain: {result['principle']}"
            )
    
    def test_confidence_weighting_affects_score(self, sample_principles):
        """Score = similarity × confidence_weight. [RULE-1-4]"""
        retriever = MockMinisterRetriever("psychology", sample_principles)
        results = retriever.retrieve("query", k=5)
        
        for result in results:
            expected_score = result["similarity"] * result["confidence_weight"]
            assert_rule(
                abs(result["score"] - expected_score) < 0.001,
                "RULE-1-4",
                f"Score not properly weighted. Expected {expected_score}, got {result['score']}"
            )
    
    def test_empty_index_graceful_failure(self):
        """Empty index returns empty list, not crash. [RULE-1-4]"""
        retriever = MockMinisterRetriever("psychology", [])
        
        try:
            results = retriever.retrieve("query", k=5)
            assert_rule(
                results == [],
                "RULE-1-4",
                f"Empty index must return empty list, got {results}"
            )
        except Exception as e:
            raise AssertionError(
                f"VIOLATION [RULE-1-4]: Empty index caused crash: {e}"
            )
    
    def test_results_sorted_by_score_descending(self, sample_principles):
        """Results sorted by score, highest first. [RULE-1-4]"""
        retriever = MockMinisterRetriever("psychology", sample_principles)
        results = retriever.retrieve("query", k=10)
        
        scores = [r["score"] for r in results]
        sorted_scores = sorted(scores, reverse=True)
        
        assert_rule(
            scores == sorted_scores,
            "RULE-1-4",
            f"Results not sorted by score descending. Got {scores}, expected {sorted_scores}"
        )
    
    def test_respects_k_limit(self, sample_principles):
        """Retriever respects k parameter. [RULE-1-4]"""
        retriever = MockMinisterRetriever("psychology", sample_principles)
        
        for k in [1, 2, 3, 5, 10]:
            results = retriever.retrieve("query", k=k)
            assert_rule(
                len(results) <= k,
                "RULE-1-4",
                f"Requested k={k} results, got {len(results)}"
            )


class TestRetrieverDomainIsolation:
    """Critical test: domain isolation is non-negotiable."""
    
    def test_psychology_power_no_crossover(self, sample_principles):
        """Psychology and power ministers never return overlapping domains. [RULE-1-5]"""
        psy_retriever = MockMinisterRetriever("psychology", sample_principles)
        pow_retriever = MockMinisterRetriever("power", sample_principles)
        
        psy_results = psy_retriever.retrieve("query", k=10)
        pow_results = pow_retriever.retrieve("query", k=10)
        
        psy_ids = {r["principle"] for r in psy_results if r["domain_fit"] == ["power"]}
        pow_ids = {r["principle"] for r in pow_results if r["domain_fit"] == ["psychology"]}
        
        assert_rule(
            len(psy_ids) == 0,
            "RULE-1-5",
            f"Psychology retriever returned power-only principles: {psy_ids}"
        )
        
        assert_rule(
            len(pow_ids) == 0,
            "RULE-1-5",
            f"Power retriever returned psychology-only principles: {pow_ids}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
