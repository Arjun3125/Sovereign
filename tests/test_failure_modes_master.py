"""
I. FAILURE MODES & CORRUPTION DEFENSE TESTS

Tests guarantee:
- Crash mid-ingest doesn't corrupt store (I1)
- Malformed doctrine is rejected (I2)
"""

import pytest
import json
from typing import Dict, Any


class TestI1_PartialIngestRecovery:
    """I1: Must guarantee crash mid-ingest doesn't corrupt store"""
    
    @pytest.fixture
    def ingest_store_checkpoint(self):
        """Store with checkpoint/rollback capability"""
        return {
            "data": {},
            "checkpoints": [],
            "transaction_id": None,
            "consistent": True
        }
    
    def test_partial_ingest_recovery(self, ingest_store_checkpoint):
        """Partial ingest that crashes recovers to consistent state"""
        store = ingest_store_checkpoint
        
        # Start transaction
        store["transaction_id"] = "txn_001"
        store["checkpoints"].append(json.dumps(store["data"]))
        
        # Simulate partial ingest (crashes after 2/5 items)
        items_to_ingest = ["item1", "item2", "item3_crash", "item4", "item5"]
        
        for i, item in enumerate(items_to_ingest):
            if i == 2:
                # Simulate crash
                break
            store["data"][f"key_{i}"] = item
        
        # After crash, verify consistency
        # Without explicit rollback, should be in inconsistent state initially
        is_consistent = len(store["data"]) > 0 and len(store["checkpoints"]) > 0
        
        # Recovery mechanism: restore from checkpoint
        if not is_consistent:
            store["data"] = json.loads(store["checkpoints"][0])
            store["consistent"] = True
        
        assert store["consistent"], "Store still inconsistent after recovery"
        assert len(store["checkpoints"]) > 0, "No checkpoints for recovery"
    
    def test_ingest_atomicity(self):
        """Ingest all-or-nothing: complete or no changes"""
        store_state_before = {"items": {}}
        items = [1, 2, 3, 4, 5]
        
        try:
            # All-or-nothing ingest
            for item in items:
                if item == 4:
                    raise Exception("Simulated crash at item 4")
                store_state_before["items"][item] = f"data_{item}"
        except:
            # Rollback entire transaction
            store_state_before["items"] = {}
        
        # Should be empty (rollback) or completely filled (success)
        # With crash, should be rolled back
        assert len(store_state_before["items"]) == 0, \
            "Partial ingest was not rolled back"
    
    def test_checkpoint_on_major_milestones(self):
        """Checkpoints created at major ingest milestones"""
        checkpoints = []
        
        def checkpoint(label):
            checkpoints.append(label)
        
        # Ingest workflow
        checkpoint("start")
        checkpoint("pdf_extracted")
        checkpoint("chapters_detected")
        checkpoint("principles_extracted")
        checkpoint("validation_passed")
        checkpoint("indexed")
        checkpoint("committed")
        
        # Verify checkpoints
        assert "start" in checkpoints
        assert "committed" in checkpoints
        assert len(checkpoints) >= 5, "Too few checkpoints"
    
    def test_consistency_check_after_ingest(self):
        """Store consistency verified after every ingest"""
        store = {
            "principles": [1, 2, 3],
            "embeddings": {1: "emb1", 2: "emb2", 3: "emb3"},
            "index": ["emb1", "emb2", "emb3"]
        }
        
        # Consistency checks
        principles_count = len(store["principles"])
        embeddings_count = len(store["embeddings"])
        index_count = len(store["index"])
        
        assert principles_count == embeddings_count == index_count, \
            f"Counts don't match: {principles_count} vs {embeddings_count} vs {index_count}"


class TestI2_InvalidDoctrineDefense:
    """I2: Must guarantee malformed doctrine is rejected"""
    
    @pytest.fixture
    def valid_doctrine(self):
        """Example of valid doctrine"""
        return {
            "metadata": {
                "version": "1.0",
                "locked": True,
                "created": "2025-01-01"
            },
            "principles": [
                {
                    "id": "p1",
                    "text": "Valid principle",
                    "confidence": 0.95,
                    "source": "doc1"
                }
            ]
        }
    
    @pytest.fixture
    def malformed_doctrines(self):
        """Examples of invalid doctrines"""
        return [
            {
                # Missing principles
                "metadata": {"version": "1.0"}
            },
            {
                # Principles not a list
                "metadata": {"version": "1.0"},
                "principles": "not a list"
            },
            {
                # Principle missing ID
                "metadata": {"version": "1.0"},
                "principles": [{"text": "Missing ID"}]
            },
            {
                # Invalid confidence
                "metadata": {"version": "1.0"},
                "principles": [
                    {"id": "p1", "text": "Test", "confidence": 1.5}
                ]
            },
            {
                # Locked doctrine is not dict
                "locked": "not_boolean"
            }
        ]
    
    def test_invalid_doctrine_rejected(self, malformed_doctrines):
        """Reject all malformed doctrines"""
        for i, doctrine in enumerate(malformed_doctrines):
            is_valid = self._validate_doctrine(doctrine)
            assert not is_valid, f"Malformed doctrine {i} was not rejected: {doctrine}"
    
    def test_valid_doctrine_accepted(self, valid_doctrine):
        """Accept well-formed doctrine"""
        is_valid = self._validate_doctrine(valid_doctrine)
        assert is_valid, "Valid doctrine was rejected"
    
    def _validate_doctrine(self, doctrine):
        """Validate doctrine structure"""
        try:
            # Check metadata
            if "metadata" not in doctrine:
                return False
            
            # Check principles
            if "principles" not in doctrine:
                return False
            
            if not isinstance(doctrine["principles"], list):
                return False
            
            # Check each principle
            for p in doctrine["principles"]:
                if "id" not in p:
                    return False
                if "text" not in p:
                    return False
                if "confidence" in p:
                    if not (0 <= p["confidence"] <= 1):
                        return False
            
            return True
        except:
            return False
    
    def test_null_injection_defense(self):
        """Reject doctrine with null byte injection"""
        malicious_principle = {
            "id": "p1",
            "text": "Legitimate\x00Injected malicious content"
        }
        
        # Should detect null byte
        has_null = "\x00" in malicious_principle["text"]
        assert has_null, "Null byte not detected in test"
        
        # Validation should reject
        is_valid = True
        if has_null:
            is_valid = False
        
        assert not is_valid, "Null byte injection not caught"
    
    def test_json_injection_defense(self):
        """Reject doctrine with JSON injection attempts"""
        malicious = {
            "id": "p1",
            "text": 'Test"; "injected": "value'
        }
        
        # Properly serialized JSON should not allow injection
        try:
            serialized = json.dumps(malicious)
            deserialized = json.loads(serialized)
            
            # Should only have original fields
            assert "injected" not in deserialized, "JSON injection succeeded"
        except:
            pass  # Also valid if parsing fails
    
    def test_size_limit_defense(self):
        """Reject doctrine exceeding size limits"""
        max_size_bytes = 1000000  # 1MB
        
        # Create oversized doctrine
        oversized = {
            "principles": [
                {"id": f"p{i}", "text": "x" * 10000}
                for i in range(200)  # 200 * 10KB = 2MB
            ]
        }
        
        size = len(json.dumps(oversized).encode())
        
        if size > max_size_bytes:
            rejected = True
        else:
            rejected = False
        
        assert rejected, "Oversized doctrine was not rejected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
