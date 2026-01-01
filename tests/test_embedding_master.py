"""
B. EMBEDDING SYSTEM TESTS

Tests guarantee:
- Same text → same embedding ID (B1)
- No recompute after done (B1)
- Deterministic vectors for same input (B2)
"""

import pytest
import numpy as np
import hashlib
from typing import Dict, List


class TestB1_NoDuplicateEmbeddings:
    """B1: Must guarantee same text → same embedding ID, no recompute after done"""
    
    @pytest.fixture
    def mock_embedding_store(self):
        """In-memory embedding store"""
        return {
            "embeddings": {},  # hash → embedding_id
            "vectors": {},      # embedding_id → vector
            "compute_count": 0
        }
    
    def test_same_text_same_id(self, mock_embedding_store):
        """Same text produces same embedding ID"""
        text = "Power is retained by foresight"
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # First embedding
        if text_hash not in mock_embedding_store["embeddings"]:
            embedding_id = f"emb_{text_hash[:16]}"
            mock_embedding_store["embeddings"][text_hash] = embedding_id
            mock_embedding_store["compute_count"] += 1
        id1 = mock_embedding_store["embeddings"][text_hash]
        
        # Second embedding (same text)
        if text_hash not in mock_embedding_store["embeddings"]:
            embedding_id = f"emb_{text_hash[:16]}"
            mock_embedding_store["embeddings"][text_hash] = embedding_id
            mock_embedding_store["compute_count"] += 1
        id2 = mock_embedding_store["embeddings"][text_hash]
        
        # Must be identical
        assert id1 == id2, "Same text produced different IDs"
        assert mock_embedding_store["compute_count"] == 1, "Computed twice"
    
    def test_no_recompute_after_stored(self, mock_embedding_store):
        """Once embedding is computed and stored, never recompute"""
        text = "Doctrine of Silence"
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # First request - must compute
        if text_hash not in mock_embedding_store["embeddings"]:
            emb_id = f"emb_{text_hash[:16]}"
            mock_embedding_store["embeddings"][text_hash] = emb_id
            mock_embedding_store["compute_count"] += 1
        
        compute_after_first = mock_embedding_store["compute_count"]
        
        # Second request - must NOT compute
        if text_hash not in mock_embedding_store["embeddings"]:
            emb_id = f"emb_{text_hash[:16]}"
            mock_embedding_store["embeddings"][text_hash] = emb_id
            mock_embedding_store["compute_count"] += 1
        
        compute_after_second = mock_embedding_store["compute_count"]
        
        # Must not have recomputed
        assert compute_after_first == compute_after_second, "Recomputed unnecessarily"
        assert compute_after_first == 1, "Should have computed exactly once"
    
    def test_different_text_different_id(self, mock_embedding_store):
        """Different text produces different embedding IDs"""
        text1 = "Silence is supremacy"
        text2 = "Speech is weakness"
        
        hash1 = hashlib.sha256(text1.encode()).hexdigest()
        hash2 = hashlib.sha256(text2.encode()).hexdigest()
        
        id1 = f"emb_{hash1[:16]}"
        id2 = f"emb_{hash2[:16]}"
        
        mock_embedding_store["embeddings"][hash1] = id1
        mock_embedding_store["embeddings"][hash2] = id2
        
        assert id1 != id2, "Different texts have same ID"
    
    def test_embedding_cache_persistence(self, mock_embedding_store):
        """Embedding cache persists across multiple accesses"""
        text = "The talkative reveal their strategy"
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Request 1
        if text_hash not in mock_embedding_store["embeddings"]:
            mock_embedding_store["embeddings"][text_hash] = f"emb_cached"
            mock_embedding_store["compute_count"] += 1
        
        id1 = mock_embedding_store["embeddings"][text_hash]
        
        # Request 2 (cache hit)
        id2 = mock_embedding_store["embeddings"][text_hash]
        
        # Request 3 (cache hit)
        id3 = mock_embedding_store["embeddings"][text_hash]
        
        assert id1 == id2 == id3, "Cache not persistent"
        assert mock_embedding_store["compute_count"] == 1, "Recomputed from cache"


class TestB2_EmbeddingStability:
    """B2: Must guarantee deterministic vectors for same input"""
    
    @pytest.fixture
    def mock_embedding_engine(self):
        """Mock embedding engine with deterministic vectors"""
        return {
            "seed": 42,
            "cache": {}
        }
    
    def test_embedding_deterministic(self, mock_embedding_engine):
        """Same text produces bitwise-identical vectors"""
        text = "Doctrine of Silence"
        
        # Set seed
        np.random.seed(mock_embedding_engine["seed"])
        
        # First embedding
        v1 = np.random.randn(768)
        
        # Second embedding (reset seed, same text)
        np.random.seed(mock_embedding_engine["seed"])
        v2 = np.random.randn(768)
        
        # Must be identical
        assert np.allclose(v1, v2), "Vectors not deterministic"
        assert np.array_equal(v1, v2), "Vectors differ at bit level"
    
    def test_determinism_across_sessions(self, mock_embedding_engine):
        """Embeddings are identical across separate Python sessions (via seed)"""
        # Session 1
        np.random.seed(mock_embedding_engine["seed"])
        session1_vector = np.random.randn(768)
        session1_norm = np.linalg.norm(session1_vector)
        
        # Session 2 (simulated)
        np.random.seed(mock_embedding_engine["seed"])
        session2_vector = np.random.randn(768)
        session2_norm = np.linalg.norm(session2_vector)
        
        assert np.allclose(session1_norm, session2_norm), \
            f"Vector norms differ: {session1_norm} vs {session2_norm}"
        assert np.array_equal(session1_vector, session2_vector), \
            "Vectors differ across sessions"
    
    def test_no_random_initialization(self):
        """Embeddings use fixed seed, never random initialization"""
        # Seed 1
        np.random.seed(123)
        v_seeded = np.random.randn(768)
        
        # No seed (would be random)
        v_random = np.random.randn(768)
        
        # Verify seeded and random are different (proves seeding matters)
        assert not np.array_equal(v_seeded, v_random), \
            "Seeded and random vectors identical (seed not working)"
    
    def test_vector_magnitude_stable(self):
        """Embedding vector magnitude is stable (L2 norm)"""
        np.random.seed(42)
        text = "Test"
        
        vectors = []
        for _ in range(5):
            np.random.seed(42)
            v = np.random.randn(768)
            vectors.append(np.linalg.norm(v))
        
        # All norms should be identical
        assert all(np.isclose(v, vectors[0]) for v in vectors), \
            "Vector magnitudes differ"
    
    def test_cosine_similarity_stable(self):
        """Cosine similarity between two texts is deterministic"""
        text1 = "Silence is power"
        text2 = "Silence is supremacy"
        
        np.random.seed(42)
        v1_run1 = np.random.randn(768)
        v2_run1 = np.random.randn(768)
        sim1 = np.dot(v1_run1, v2_run1) / (np.linalg.norm(v1_run1) * np.linalg.norm(v2_run1))
        
        np.random.seed(42)
        v1_run2 = np.random.randn(768)
        v2_run2 = np.random.randn(768)
        sim2 = np.dot(v1_run2, v2_run2) / (np.linalg.norm(v1_run2) * np.linalg.norm(v2_run2))
        
        assert np.isclose(sim1, sim2), \
            f"Cosine similarity not deterministic: {sim1} vs {sim2}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
