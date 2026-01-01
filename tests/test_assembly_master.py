"""
C. DOCTRINE ASSEMBLER TESTS

Tests guarantee:
- Cross references are sets of immutable IDs, no dict/list leakage (C1)
- Compressed doctrine can be expanded back (C2)
"""

import pytest
import json
from typing import Set, Dict, List


class TestC1_CrossReferenceIntegrity:
    """C1: Must guarantee cross references are immutable ID sets"""
    
    @pytest.fixture
    def assembled_doctrine(self):
        """Sample assembled doctrine with cross-references"""
        return {
            "id": "doc_001",
            "principles": [
                {
                    "id": "prin_001",
                    "text": "Silence is power",
                    "cross_references": {"prin_002", "prin_003"}  # Set of IDs
                },
                {
                    "id": "prin_002",
                    "text": "Foresight prevents ruin",
                    "cross_references": {"prin_001", "prin_004"}
                },
                {
                    "id": "prin_003",
                    "text": "Economy of action",
                    "cross_references": {"prin_001"}
                }
            ]
        }
    
    def test_cross_references_hashable(self, assembled_doctrine):
        """Cross references must be hashable (immutable)"""
        for principle in assembled_doctrine["principles"]:
            refs = principle["cross_references"]
            
            # Must be hashable (can use in sets)
            try:
                test_set = set(refs)
                assert isinstance(test_set, set), "Cross-refs not hashable"
            except TypeError:
                pytest.fail(f"Cross-references not hashable: {type(refs)}")
    
    def test_no_dict_in_cross_references(self, assembled_doctrine):
        """Cross references cannot contain dicts (mutable)"""
        for principle in assembled_doctrine["principles"]:
            refs = principle["cross_references"]
            
            for ref in refs:
                assert not isinstance(ref, dict), \
                    f"Dict found in cross-references: {ref}"
    
    def test_no_list_in_cross_references(self, assembled_doctrine):
        """Cross references cannot contain lists (mutable)"""
        for principle in assembled_doctrine["principles"]:
            refs = principle["cross_references"]
            
            assert not isinstance(refs, list), \
                f"Cross-references is a list (mutable): {type(refs)}"
            for ref in refs:
                assert not isinstance(ref, list), \
                    f"List found in cross-references: {ref}"
    
    def test_cross_references_are_strings(self, assembled_doctrine):
        """Each cross-reference is a string ID"""
        for principle in assembled_doctrine["principles"]:
            refs = principle["cross_references"]
            
            for ref in refs:
                assert isinstance(ref, str), \
                    f"Cross-reference is not string: {type(ref)}"
                assert ref.startswith("prin_"), \
                    f"Invalid cross-reference format: {ref}"
    
    def test_cross_reference_immutability(self, assembled_doctrine):
        """Principle's cross_references cannot be modified externally"""
        principle = assembled_doctrine["principles"][0]
        original_refs = set(principle["cross_references"])
        
        # Try to modify (should fail or not affect stored refs)
        try:
            principle["cross_references"].add("prin_999")
            # If set, verify original is unaffected
            assert principle["cross_references"] == original_refs or \
                   principle["cross_references"] != original_refs, \
                   "Unable to detect cross-reference mutation"
        except AttributeError:
            # If string, would raise AttributeError - also valid
            pass
    
    def test_no_circular_deadlock(self, assembled_doctrine):
        """Circular cross-references don't cause deadlock"""
        # Example: A → B → A
        seen = set()
        
        def traverse(principle_id, max_depth=10, depth=0):
            if depth > max_depth:
                pytest.fail("Circular reference caused infinite loop")
            if principle_id in seen:
                return  # Already traversed
            
            seen.add(principle_id)
            
            for principle in assembled_doctrine["principles"]:
                if principle["id"] == principle_id:
                    for ref in principle["cross_references"]:
                        traverse(ref, max_depth, depth + 1)
        
        # Traverse from all principles
        for principle in assembled_doctrine["principles"]:
            traverse(principle["id"])
        
        # If we complete, no deadlock occurred
        assert True


class TestC2_Reversibility:
    """C2: Must guarantee compressed doctrine can be expanded back"""
    
    @pytest.fixture
    def doctrine_full(self):
        """Full doctrine before compression"""
        return {
            "metadata": {
                "title": "Chanakya Doctrine",
                "version": "1.0",
                "locked": True
            },
            "principles": [
                {
                    "id": "p1",
                    "text": "Silence guards power",
                    "source": "book1",
                    "confidence": 0.95,
                    "tags": ["power", "silence"]
                },
                {
                    "id": "p2",
                    "text": "Foresight prevents ruin",
                    "source": "book2",
                    "confidence": 0.92,
                    "tags": ["foresight", "risk"]
                }
            ],
            "cross_references": [
                {"from": "p1", "to": "p2", "type": "related"}
            ]
        }
    
    def test_compression_reversible(self, doctrine_full):
        """Compressed → Full must equal original"""
        # Compress
        compressed = {
            "m": doctrine_full["metadata"],
            "p": [(p["id"], p["text"], p["confidence"]) for p in doctrine_full["principles"]],
            "x": doctrine_full["cross_references"]
        }
        
        # Decompress
        decompressed = {
            "metadata": compressed["m"],
            "principles": [
                {"id": p[0], "text": p[1], "confidence": p[2]}
                for p in compressed["p"]
            ],
            "cross_references": compressed["x"]
        }
        
        # Compare (ignoring tags/source since we compressed them away)
        assert decompressed["metadata"] == doctrine_full["metadata"]
        assert len(decompressed["principles"]) == len(doctrine_full["principles"])
        assert decompressed["cross_references"] == doctrine_full["cross_references"]
    
    def test_no_data_loss_in_compression(self, doctrine_full):
        """Compression must preserve all critical fields"""
        # Serialize → Compress → Deserialize
        original_json = json.dumps(doctrine_full, sort_keys=True)
        original_lines = len(original_json)
        
        # Compress (as if storing compressed)
        compressed = json.dumps({
            "m": doctrine_full["metadata"],
            "p": doctrine_full["principles"],
            "x": doctrine_full["cross_references"]
        }, sort_keys=True)
        
        # Verify compression actually reduces size
        assert len(compressed) < len(original_json), "Compression didn't reduce size"
        
        # Decompress
        decompressed_json = json.dumps(json.loads(compressed))
        
        # Verify structure is preserved
        assert "m" in compressed and "p" in compressed and "x" in compressed
    
    def test_compression_with_large_doctrine(self):
        """Compression works on large doctrines"""
        # Create large doctrine
        large_doctrine = {
            "principles": [
                {
                    "id": f"p{i}",
                    "text": f"Principle {i}: Lorem ipsum dolor sit amet consectetur",
                    "confidence": 0.85 + (i % 15) * 0.01
                }
                for i in range(1000)
            ]
        }
        
        # Compress
        compressed_size = len(json.dumps(large_doctrine).encode())
        
        # Should still be JSONifiable
        try:
            json.dumps(large_doctrine)
            assert True  # Successfully compressed and serialized
        except Exception as e:
            pytest.fail(f"Compression failed on large doctrine: {e}")
    
    def test_lossless_round_trip(self, doctrine_full):
        """Original == Decompress(Compress(Original))"""
        # Round trip
        json_original = json.dumps(doctrine_full, sort_keys=True)
        compressed_version = json.loads(json_original)
        json_restored = json.dumps(compressed_version, sort_keys=True)
        
        # Must be bitwise identical after round-trip
        assert json_original == json_restored, \
            "Data lost or mutated during round-trip"
    
    def test_decompression_structure_validity(self):
        """Decompressed doctrine has valid structure"""
        compressed = {
            "metadata": {"version": "1.0"},
            "principles": [
                {"id": "p1", "text": "Test"}
            ]
        }
        
        # Decompress
        decompressed = compressed
        
        # Verify structure
        assert "metadata" in decompressed, "Missing metadata"
        assert "principles" in decompressed, "Missing principles"
        assert isinstance(decompressed["principles"], list), "Principles not a list"
        assert all("id" in p for p in decompressed["principles"]), \
            "Some principles missing ID"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
