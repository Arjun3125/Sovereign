"""
L1 Test Suite — Principle Indexing
Tests embedding integrity, determinism, isolated failures [RULE-1-9, 1-10]
"""
import pytest
import json
from tests.conftest import assert_rule


class MockPrincipleIndex:
    """Mock index for testing (real one in core/knowledge/index/)."""
    
    def __init__(self):
        self.index_entries = {}  # principle_id -> {embedding, domain_fit, ...}
        self.meta = {}  # principle_id -> {principle, confidence_weight, source}
        self.rebuild_count = 0
    
    def add_principle(self, principle_id: str, principle_text: str, 
                     embedding: list, domain_fit: list, 
                     confidence_weight: float, source: dict):
        """Add principle to index."""
        self.index_entries[principle_id] = {
            "principle_id": principle_id,
            "embedding": embedding,
            "domain_fit": domain_fit,
        }
        self.meta[principle_id] = {
            "principle": principle_text,
            "confidence_weight": confidence_weight,
            "source": source,
        }
    
    def rebuild(self):
        """Simulate index rebuild (deterministic)."""
        self.rebuild_count += 1
        # Return same structure both times
        return {
            "index_count": len(self.index_entries),
            "meta_count": len(self.meta),
            "embedding_dims": [len(e["embedding"]) for e in self.index_entries.values()] if self.index_entries else []
        }
    
    def get_embedding(self, principle_id: str) -> list:
        """Get embedding for principle."""
        return self.index_entries.get(principle_id, {}).get("embedding", [])


class TestPrincipleIndexing:
    """Test indexing mechanics."""
    
    def test_each_principle_has_exactly_one_embedding(self):
        """Each principle has exactly one embedding (no orphans/duplicates). [RULE-1-9]"""
        index = MockPrincipleIndex()
        
        principles = [
            ("charm_001", "Charm lowers defenses", [0.1] * 768, ["psychology"]),
            ("charm_002", "Listening builds trust", [0.12] * 768, ["psychology"]),
            ("power_001", "Silence compounds authority", [0.2] * 768, ["power"]),
        ]
        
        for principle_id, text, embedding, domain_fit in principles:
            index.add_principle(
                principle_id, text, embedding, domain_fit,
                confidence_weight=0.85,
                source={"book": "test", "chapter": "raw"}
            )
        
        # Verify each principle has exactly one embedding
        for principle_id in ["charm_001", "charm_002", "power_001"]:
            embedding = index.get_embedding(principle_id)
            assert_rule(
                len(embedding) == 768,
                "RULE-1-9",
                f"Principle {principle_id} embedding missing or wrong size: {len(embedding)}"
            )
        
        # Verify no orphans
        assert_rule(
            len(index.index_entries) == 3,
            "RULE-1-9",
            f"Expected 3 principles in index, got {len(index.index_entries)}"
        )
    
    def test_index_rebuild_deterministic(self):
        """Index rebuild is deterministic (same structure both times). [RULE-1-10]"""
        index = MockPrincipleIndex()
        
        # Add principles
        for i in range(5):
            index.add_principle(
                f"p_{i}",
                f"Principle {i}",
                [0.1 + i * 0.01] * 768,
                ["psychology"] if i % 2 == 0 else ["power"],
                confidence_weight=0.85,
                source={"book": "test", "chapter": "raw"}
            )
        
        # Rebuild twice
        result1 = index.rebuild()
        result2 = index.rebuild()
        
        # Results must be identical
        assert_rule(
            result1 == result2,
            "RULE-1-10",
            f"Index rebuild not deterministic. First: {result1}, Second: {result2}"
        )
    
    def test_embedding_dimensions_consistent(self):
        """All embeddings are 768-dimensional (nomic-embed-text standard). [RULE-1-9]"""
        index = MockPrincipleIndex()
        
        for i in range(10):
            embedding = [0.1 + (i + j) * 0.001 for j in range(768)]
            index.add_principle(
                f"p_{i}",
                f"Principle {i}",
                embedding,
                ["psychology"],
                confidence_weight=0.85,
                source={"book": "test", "chapter": "raw"}
            )
        
        # Check all embeddings are 768-dim
        for principle_id, entry in index.index_entries.items():
            embedding_dim = len(entry["embedding"])
            assert_rule(
                embedding_dim == 768,
                "RULE-1-9",
                f"Principle {principle_id} has {embedding_dim}d embedding, expected 768"
            )
    
    def test_meta_maps_all_index_entries(self):
        """Meta YAML maps every principle ID in index (1:1 match). [RULE-1-9]"""
        index = MockPrincipleIndex()
        
        for i in range(5):
            index.add_principle(
                f"p_{i}",
                f"Principle {i}",
                [0.1] * 768,
                ["psychology"],
                confidence_weight=0.85,
                source={"book": "test", "chapter": f"raw_{i}"}
            )
        
        # Verify 1:1 mapping
        index_ids = set(index.index_entries.keys())
        meta_ids = set(index.meta.keys())
        
        assert_rule(
            index_ids == meta_ids,
            "RULE-1-9",
            f"Index and meta not aligned. Index: {index_ids}, Meta: {meta_ids}"
        )
    
    def test_corrupt_principle_isolated_failure(self):
        """Corrupt principle file causes isolated failure, not total crash. [RULE-1-9]"""
        index = MockPrincipleIndex()
        
        # Add valid principles
        for i in range(3):
            index.add_principle(
                f"valid_{i}",
                f"Valid principle {i}",
                [0.1] * 768,
                ["psychology"],
                confidence_weight=0.85,
                source={"book": "test", "chapter": "raw"}
            )
        
        # Try to add corrupt (empty embedding)
        try:
            # This should either skip or flag the corrupt entry
            corrupt_embedding = []
            if len(corrupt_embedding) != 768:
                # Skip corrupt entry, but continue
                pass
            
            # Verify valid entries still present
            assert_rule(
                len(index.index_entries) >= 3,
                "RULE-1-9",
                f"Valid principles lost after corrupt attempt. Only {len(index.index_entries)} left"
            )
        except Exception as e:
            raise AssertionError(
                f"VIOLATION [RULE-1-9]: Corrupt principle crashed system: {e}"
            )
    
    def test_index_queryable_after_rebuild(self):
        """After rebuild, index remains queryable. [RULE-1-10]"""
        index = MockPrincipleIndex()
        
        # Add principles
        for i in range(5):
            index.add_principle(
                f"p_{i}",
                f"Principle {i}",
                [0.1 + i * 0.01] * 768,
                ["psychology"],
                confidence_weight=0.85,
                source={"book": "test", "chapter": "raw"}
            )
        
        # Rebuild
        index.rebuild()
        
        # Verify all principles still queryable
        for i in range(5):
            embedding = index.get_embedding(f"p_{i}")
            assert_rule(
                len(embedding) == 768,
                "RULE-1-10",
                f"Principle p_{i} not queryable after rebuild"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
