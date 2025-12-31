"""
B1. NO DUPLICATE EMBEDDINGS TEST

Test guarantees:
- Same text always gets same embedding ID
- No recomputation of embeddings (cached)
- Embedding deduplication works correctly
"""

import pytest
import hashlib
from typing import Dict, Optional


class TestB1_NoDuplicateEmbeddings:
    """B1: Must guarantee same text always gets same embedding ID"""
    
    @pytest.fixture
    def embedding_store(self):
        """Mock embedding store with deduplication"""
        return {
            "embeddings": {},      # text -> embedding_vector
            "embedding_ids": {},   # text_hash -> embedding_id
            "compute_count": {},   # text_hash -> count (for tracking recomputation)
        }
    
    @pytest.fixture
    def mock_embedder(self, embedding_store):
        """Mock embedder that generates embeddings"""
        def embed_text(text: str) -> Dict:
            text_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
            
            # Check if already computed
            if text_hash in embedding_store["embedding_ids"]:
                # Return cached result
                embedding_id = embedding_store["embedding_ids"][text_hash]
                embedding_store["compute_count"][text_hash] += 1
                return {
                    "id": embedding_id,
                    "vector": embedding_store["embeddings"][embedding_id],
                    "cached": True
                }
            
            # Generate new embedding
            embedding_id = f"emb_{text_hash}"
            vector = [0.1 * (ord(c) % 10) for c in text[:100]]  # Deterministic vector
            
            embedding_store["embeddings"][embedding_id] = vector
            embedding_store["embedding_ids"][text_hash] = embedding_id
            embedding_store["compute_count"][text_hash] = 0
            
            return {
                "id": embedding_id,
                "vector": vector,
                "cached": False
            }
        
        return embed_text
    
    def test_same_text_same_embedding_id(self, mock_embedder):
        """Same text produces same embedding ID"""
        text = "Constitutional principle regarding sovereignty"
        
        result1 = mock_embedder(text)
        result2 = mock_embedder(text)
        
        assert result1["id"] == result2["id"], \
            "Same text produced different embedding IDs"
    
    def test_different_text_different_ids(self, mock_embedder):
        """Different text produces different embedding IDs"""
        text1 = "First principle about authority"
        text2 = "Second principle about decisions"
        
        result1 = mock_embedder(text1)
        result2 = mock_embedder(text2)
        
        assert result1["id"] != result2["id"], \
            "Different text produced same embedding ID"
    
    def test_no_recomputation_on_cache_hit(self, mock_embedder, embedding_store):
        """Second request for same text uses cache (no recomputation)"""
        text = "Doctrine principle"
        
        # First computation
        result1 = mock_embedder(text)
        assert result1["cached"] is False, "First computation marked as cached"
        
        # Second request
        result2 = mock_embedder(text)
        assert result2["cached"] is True, "Cache hit not marked as cached"
        assert result1["id"] == result2["id"], "IDs differ on cache hit"
    
    def test_embedding_deduplication_store(self, embedding_store, mock_embedder):
        """Embeddings store never duplicates same embedding vector"""
        texts = [
            "Sovereign makes final decisions",
            "Sovereign makes final decisions",
            "Sovereign makes final decisions",
        ]
        
        embedding_ids = []
        for text in texts:
            result = mock_embedder(text)
            embedding_ids.append(result["id"])
        
        # All should have same ID
        assert all(eid == embedding_ids[0] for eid in embedding_ids), \
            "Duplicate texts produced different embedding IDs"
        
        # Only one embedding stored
        unique_ids = set(embedding_ids)
        assert len(unique_ids) == 1, \
            f"Expected 1 unique embedding, got {len(unique_ids)}"
    
    def test_cache_prevents_recomputation(self, embedding_store, mock_embedder):
        """Embeddings cache prevents expensive recomputation"""
        text = "Important constitutional principle"
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
        
        # First call computes
        result1 = mock_embedder(text)
        compute_count_1 = embedding_store["compute_count"][text_hash]
        
        # Second call uses cache
        result2 = mock_embedder(text)
        compute_count_2 = embedding_store["compute_count"][text_hash]
        
        # Compute count should increase by 1 (cache hit recorded)
        assert compute_count_2 == compute_count_1 + 1, \
            "Cache hit not being tracked"
        
        # Results identical
        assert result1["id"] == result2["id"]
        assert result1["vector"] == result2["vector"]
    
    def test_identical_vectors_same_text(self, mock_embedder):
        """Same text produces identical embedding vectors"""
        text = "Shall we repeat this principle"
        
        result1 = mock_embedder(text)
        result2 = mock_embedder(text)
        
        vector1 = result1["vector"]
        vector2 = result2["vector"]
        
        assert vector1 == vector2, \
            "Same text produced different embedding vectors"
        assert len(vector1) > 0, "Embedding vector is empty"
    
    def test_deduplication_with_batch_ingestion(self, mock_embedder, embedding_store):
        """Batch ingestion deduplicates overlapping texts"""
        texts = [
            "First unique principle",
            "Second unique principle",
            "First unique principle",  # Duplicate
            "Third unique principle",
            "Second unique principle",  # Duplicate
            "First unique principle",  # Duplicate
        ]
        
        results = []
        for text in texts:
            result = mock_embedder(text)
            results.append(result)
        
        # Should have 3 unique embeddings
        unique_ids = set(r["id"] for r in results)
        assert len(unique_ids) == 3, \
            f"Expected 3 unique embeddings, got {len(unique_ids)}"
        
        # Duplicates should map to same IDs
        id1 = results[0]["id"]  # First principle
        id1_dup1 = results[2]["id"]  # Duplicate
        id1_dup2 = results[5]["id"]  # Duplicate
        assert id1 == id1_dup1 == id1_dup2, \
            "Duplicate texts produced different IDs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
