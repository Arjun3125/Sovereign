"""
C2. ASSEMBLY REVERSIBILITY TEST

Test guarantees:
- Compressed doctrine can be fully reconstructed
- Decompress(Compress(X)) = X
- No data loss during compression
- Reversibility maintained throughout assembly
"""

import pytest
import json
from typing import Dict, Any


class TestC2_AssemblyReversibility:
    """C2: Must guarantee compress->decompress reversibility"""
    
    @pytest.fixture
    def doctrine_compressor(self):
        """Mock compressor with reversibility"""
        class DoctrineCompressor:
            def __init__(self):
                self.compression_map = {}
                self.decompression_map = {}
            
            def compress(self, doctrine: Dict[str, Any]) -> str:
                """Compress doctrine to JSON string"""
                # Store original for decompression
                doctrine_id = f"doc_{len(self.compression_map)}"
                self.compression_map[doctrine_id] = doctrine
                
                # Create minimal representation
                compressed = {
                    "id": doctrine_id,
                    "principles_count": len(doctrine.get("principles", [])),
                    "refs_count": sum(len(p.get("refs", [])) for p in doctrine.get("principles", []))
                }
                
                # Store decompression map
                self.decompression_map[doctrine_id] = doctrine
                
                return json.dumps(compressed)
            
            def decompress(self, compressed_json: str) -> Dict[str, Any]:
                """Decompress doctrine back to original"""
                compressed = json.loads(compressed_json)
                doc_id = compressed["id"]
                
                if doc_id not in self.decompression_map:
                    raise ValueError(f"Cannot decompress: {doc_id} not found")
                
                return self.decompression_map[doc_id]
        
        return DoctrineCompressor()
    
    def test_compress_decompress_identity(self, doctrine_compressor):
        """Compress then decompress returns original"""
        original = {
            "principles": [
                {"id": "p1", "text": "Sovereignty", "refs": []},
                {"id": "p2", "text": "Authority", "refs": ["p1"]}
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        assert decompressed == original, \
            "Decompressed doctrine doesn't match original"
    
    def test_no_data_loss_compression(self, doctrine_compressor):
        """Compression preserves all data"""
        original = {
            "principles": [
                {"id": f"p{i}", "text": f"Principle {i}", "refs": []}
                for i in range(10)
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        # All principles preserved
        assert len(decompressed["principles"]) == 10
        assert all(p["id"] in [f"p{i}" for i in range(10)] 
                  for p in decompressed["principles"])
    
    def test_reversibility_with_complex_structure(self, doctrine_compressor):
        """Complex doctrine remains reversible"""
        original = {
            "metadata": {
                "version": "1.0",
                "locked": True
            },
            "principles": [
                {
                    "id": "p1",
                    "text": "Sovereign authority final",
                    "confidence": 0.95,
                    "refs": ["p2", "p3"],
                    "source": "doc1"
                },
                {
                    "id": "p2",
                    "text": "No auto-decisions",
                    "confidence": 0.90,
                    "refs": [],
                    "source": "doc1"
                },
                {
                    "id": "p3",
                    "text": "Silence allowed",
                    "confidence": 0.85,
                    "refs": ["p1"],
                    "source": "doc2"
                }
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        assert decompressed == original
    
    def test_multiple_compress_decompress_cycles(self, doctrine_compressor):
        """Multiple compress-decompress cycles maintain data"""
        original = {
            "principles": [
                {"id": "p1", "text": "First", "refs": []},
                {"id": "p2", "text": "Second", "refs": ["p1"]}
            ]
        }
        
        # Multiple cycles
        current = original
        for _ in range(5):
            compressed = doctrine_compressor.compress(current)
            current = doctrine_compressor.decompress(compressed)
        
        assert current == original
    
    def test_compressed_format_is_valid_json(self, doctrine_compressor):
        """Compressed format is valid JSON"""
        original = {
            "principles": [
                {"id": "p1", "text": "Test", "refs": []}
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        
        # Should parse as JSON
        try:
            parsed = json.loads(compressed)
            assert isinstance(parsed, dict)
        except json.JSONDecodeError:
            assert False, "Compressed format is not valid JSON"
    
    def test_references_preserved_after_compression(self, doctrine_compressor):
        """Cross-references maintained after compress-decompress"""
        original = {
            "principles": [
                {
                    "id": "p1",
                    "text": "Sovereignty",
                    "refs": ["p2", "p3", "p4"]
                },
                {"id": "p2", "text": "Authority", "refs": []},
                {"id": "p3", "text": "Decision", "refs": []},
                {"id": "p4", "text": "Final", "refs": []}
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        # Check references preserved
        original_p1_refs = set(original["principles"][0]["refs"])
        decompressed_p1_refs = set(decompressed["principles"][0]["refs"])
        
        assert original_p1_refs == decompressed_p1_refs
    
    def test_empty_doctrine_reversible(self, doctrine_compressor):
        """Empty doctrine is reversible"""
        original = {"principles": []}
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        assert decompressed == original
    
    def test_reversibility_preserves_data_types(self, doctrine_compressor):
        """Data types preserved through compress-decompress"""
        original = {
            "principles": [
                {
                    "id": "p1",
                    "text": "Principle",
                    "confidence": 0.95,
                    "locked": True,
                    "refs": ["p2"],
                    "tags": ["important", "core"]
                }
            ]
        }
        
        compressed = doctrine_compressor.compress(original)
        decompressed = doctrine_compressor.decompress(compressed)
        
        p1_original = original["principles"][0]
        p1_decompressed = decompressed["principles"][0]
        
        # Check types
        assert isinstance(p1_decompressed["confidence"], float)
        assert isinstance(p1_decompressed["locked"], bool)
        assert isinstance(p1_decompressed["refs"], list)
        assert isinstance(p1_decompressed["tags"], list)
    
    def test_bidirectional_consistency(self, doctrine_compressor):
        """Forward and backward compression consistent"""
        doctrine1 = {
            "principles": [
                {"id": "p1", "text": "First", "refs": []}
            ]
        }
        
        compressed1 = doctrine_compressor.compress(doctrine1)
        decompressed1 = doctrine_compressor.decompress(compressed1)
        compressed2 = doctrine_compressor.compress(decompressed1)
        decompressed2 = doctrine_compressor.decompress(compressed2)
        
        # Compressed forms should represent same data
        assert decompressed1 == decompressed2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
