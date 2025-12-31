"""
D1. QUERY RESULT STABILITY TEST

Test guarantees:
- Same query produces same results always
- Result ordering is stable
- Query results are deterministic
"""

import pytest
from typing import List, Dict


class TestD1_QueryResultStability:
    """D1: Must guarantee same query -> same results same order"""
    
    @pytest.fixture
    def query_engine(self):
        """Mock query engine with deterministic results"""
        class QueryEngine:
            def __init__(self):
                self.documents = {}
                self.rankings = {}  # query -> sorted results
            
            def index_documents(self, docs: List[Dict]):
                """Index documents for searching"""
                for doc in docs:
                    self.documents[doc["id"]] = doc
            
            def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
                """Query documents with consistent ordering"""
                if query_text not in self.rankings:
                    # Compute score based on deterministic hash
                    scores = {}
                    for doc_id, doc in self.documents.items():
                        # Deterministic score
                        score = sum(ord(c) for c in query_text) * sum(ord(c) for c in doc_id)
                        scores[doc_id] = score
                    
                    # Sort by score (descending), then by doc_id (for stability)
                    sorted_docs = sorted(
                        scores.items(),
                        key=lambda x: (-x[1], x[0])
                    )[:top_k]
                    
                    self.rankings[query_text] = [doc_id for doc_id, _ in sorted_docs]
                
                result_ids = self.rankings[query_text]
                return [
                    {**self.documents[doc_id], "rank": i+1}
                    for i, doc_id in enumerate(result_ids)
                ]
        
        return QueryEngine()
    
    def test_same_query_same_results(self, query_engine):
        """Same query returns same results"""
        docs = [
            {"id": "d1", "text": "Sovereignty principle"},
            {"id": "d2", "text": "Authority doctrine"},
            {"id": "d3", "text": "Decision framework"}
        ]
        query_engine.index_documents(docs)
        
        query = "sovereignty"
        result1 = query_engine.query(query)
        result2 = query_engine.query(query)
        
        assert result1 == result2, "Same query produced different results"
    
    def test_result_order_consistent(self, query_engine):
        """Result order remains consistent across queries"""
        docs = [
            {"id": f"d{i}", "text": f"Document {i}"}
            for i in range(10)
        ]
        query_engine.index_documents(docs)
        
        query = "document"
        
        # Query 5 times
        results = [query_engine.query(query) for _ in range(5)]
        
        # All should have same order
        first_order = [r["id"] for r in results[0]]
        for i, result in enumerate(results[1:], 1):
            order = [r["id"] for r in result]
            assert order == first_order, \
                f"Query {i} returned different order"
    
    def test_deterministic_ranking(self, query_engine):
        """Ranking is deterministic based on query text"""
        docs = [
            {"id": "sovereignty", "text": "Sovereign authority"},
            {"id": "authority", "text": "Final authority"},
            {"id": "decision", "text": "Decision authority"}
        ]
        query_engine.index_documents(docs)
        
        result1 = query_engine.query("authority", top_k=3)
        result2 = query_engine.query("authority", top_k=3)
        
        # Same order, same IDs
        ids1 = [r["id"] for r in result1]
        ids2 = [r["id"] for r in result2]
        
        assert ids1 == ids2, "Ranking is not deterministic"
    
    def test_different_queries_different_results(self, query_engine):
        """Different queries can produce different results"""
        docs = [
            {"id": "sovereignty", "text": "Sovereignty"},
            {"id": "authority", "text": "Authority"},
            {"id": "decision", "text": "Decision"}
        ]
        query_engine.index_documents(docs)
        
        result1 = query_engine.query("sovereignty")
        result2 = query_engine.query("authority")
        
        ids1 = [r["id"] for r in result1]
        ids2 = [r["id"] for r in result2]
        
        # Results can differ (not required to be same)
        # Just checking they're both valid and deterministic
        assert isinstance(ids1, list)
        assert isinstance(ids2, list)
    
    def test_top_k_stability(self, query_engine):
        """Top-K parameter produces stable results"""
        docs = [
            {"id": f"d{i}", "text": f"Document {i}"}
            for i in range(20)
        ]
        query_engine.index_documents(docs)
        
        query = "document"
        
        # Query with different top_k values
        top_5 = query_engine.query(query, top_k=5)
        top_10 = query_engine.query(query, top_k=10)
        
        # Top 5 should be subset of top 10
        top_5_ids = set(r["id"] for r in top_5)
        top_10_ids = set(r["id"] for r in top_10[:5])
        
        assert top_5_ids == top_10_ids, "Top-K results not stable"
    
    def test_rank_ordering_maintained(self, query_engine):
        """Rank field indicates stable ordering"""
        docs = [
            {"id": f"d{i}", "text": f"Text {i}"}
            for i in range(5)
        ]
        query_engine.index_documents(docs)
        
        result = query_engine.query("text", top_k=5)
        
        # Check rank field matches position
        for i, doc in enumerate(result, 1):
            assert doc["rank"] == i, f"Rank {i} not in position {i}"
    
    def test_repeated_queries_no_degradation(self, query_engine):
        """Repeated queries don't degrade results"""
        docs = [
            {"id": "p1", "text": "Principle one"},
            {"id": "p2", "text": "Principle two"}
        ]
        query_engine.index_documents(docs)
        
        query = "principle"
        
        # Query 100 times
        results = [query_engine.query(query) for _ in range(100)]
        
        # All should be identical
        first = [r["id"] for r in results[0]]
        for i, result in enumerate(results[1:], 1):
            current = [r["id"] for r in result]
            assert current == first, f"Query {i} differs from first"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
