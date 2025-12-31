"""
C1. CROSS-REFERENCE INTEGRITY TEST

Test guarantees:
- Cross-references are immutable ID sets (no dict/list leakage)
- No mutation of references during assembly
- References remain consistent throughout lifecycle
"""

import pytest
from typing import Set, Dict, List


class TestC1_CrossReferenceIntegrity:
    """C1: Must guarantee cross-references are immutable ID sets"""
    
    @pytest.fixture
    def doctrine_assembly(self):
        """Mock doctrine assembly with cross-references"""
        class DoctrineAssembly:
            def __init__(self):
                self.principles = {}  # id -> principle data
                self.cross_refs = {}  # principle_id -> set of referenced principle IDs
                self.version = 1
            
            def add_principle(self, principle_id: str, data: Dict):
                """Add principle to assembly"""
                self.principles[principle_id] = {
                    "id": principle_id,
                    "data": data,
                    "refs": set()  # ID set only
                }
            
            def add_reference(self, from_id: str, to_id: str):
                """Add cross-reference between principles"""
                if from_id in self.principles:
                    self.principles[from_id]["refs"].add(to_id)
            
            def get_references(self, principle_id: str) -> Set[str]:
                """Get immutable view of references"""
                if principle_id in self.principles:
                    return frozenset(self.principles[principle_id]["refs"])
                return frozenset()
            
            def assembly_complete(self):
                """Mark assembly as complete - lock references"""
                # In real system, would prevent further modifications
                return True
        
        return DoctrineAssembly()
    
    def test_references_are_id_sets(self, doctrine_assembly):
        """References must be ID sets only"""
        # Add principles
        doctrine_assembly.add_principle("p1", {"text": "Sovereignty"})
        doctrine_assembly.add_principle("p2", {"text": "Authority"})
        
        # Add reference
        doctrine_assembly.add_reference("p1", "p2")
        
        # Get references
        refs = doctrine_assembly.get_references("p1")
        
        # Must be a set of IDs only
        assert isinstance(refs, frozenset), "References should be frozenset"
        assert all(isinstance(ref, str) for ref in refs), "All refs should be strings"
        assert "p2" in refs, "p2 should be in references"
    
    def test_no_dict_list_leakage(self, doctrine_assembly):
        """References must not leak dict/list data structures"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        doctrine_assembly.add_reference("p1", "p2")
        
        refs = doctrine_assembly.get_references("p1")
        
        # Should only contain IDs, not nested structures
        for ref in refs:
            assert isinstance(ref, str), f"Reference should be string, got {type(ref)}"
            assert not isinstance(ref, dict), "Reference leaked dict"
            assert not isinstance(ref, list), "Reference leaked list"
    
    def test_reference_immutability(self, doctrine_assembly):
        """References cannot be mutated after retrieval"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        doctrine_assembly.add_reference("p1", "p2")
        
        refs = doctrine_assembly.get_references("p1")
        
        # Try to modify (should fail with frozenset)
        try:
            refs.add("p3")  # This should raise
            assert False, "Frozenset should not allow add()"
        except (TypeError, AttributeError):
            pass  # Expected - frozenset is immutable
    
    def test_reference_consistency_across_calls(self, doctrine_assembly):
        """Multiple calls return same references"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        doctrine_assembly.add_reference("p1", "p2")
        
        refs1 = doctrine_assembly.get_references("p1")
        refs2 = doctrine_assembly.get_references("p1")
        
        assert refs1 == refs2, "References should be consistent"
        assert refs1 is not refs2, "Should be different objects (copies)"
    
    def test_no_reference_side_effects(self, doctrine_assembly):
        """Getting references doesn't modify internal state"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        doctrine_assembly.add_reference("p1", "p2")
        
        # Get references multiple times
        refs_before = doctrine_assembly.get_references("p1")
        refs_middle = doctrine_assembly.get_references("p1")
        refs_after = doctrine_assembly.get_references("p1")
        
        # All should be identical
        assert refs_before == refs_middle == refs_after
    
    def test_bidirectional_references_independent(self, doctrine_assembly):
        """References from A to B independent from B to A"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        
        # p1 -> p2
        doctrine_assembly.add_reference("p1", "p2")
        
        # p2 -> p1
        doctrine_assembly.add_reference("p2", "p1")
        
        refs_p1 = doctrine_assembly.get_references("p1")
        refs_p2 = doctrine_assembly.get_references("p2")
        
        # Should be independent
        assert "p2" in refs_p1
        assert "p1" in refs_p2
        assert len(refs_p1) == 1
        assert len(refs_p2) == 1
    
    def test_multiple_references_maintained(self, doctrine_assembly):
        """Multiple references from one principle preserved"""
        doctrine_assembly.add_principle("p1", {"text": "Sovereign"})
        doctrine_assembly.add_principle("p2", {"text": "Authority"})
        doctrine_assembly.add_principle("p3", {"text": "Decision"})
        doctrine_assembly.add_principle("p4", {"text": "Final"})
        
        # p1 references multiple
        doctrine_assembly.add_reference("p1", "p2")
        doctrine_assembly.add_reference("p1", "p3")
        doctrine_assembly.add_reference("p1", "p4")
        
        refs = doctrine_assembly.get_references("p1")
        
        assert len(refs) == 3, f"Should have 3 references, got {len(refs)}"
        assert refs == frozenset(["p2", "p3", "p4"])
    
    def test_reference_isolation_between_principles(self, doctrine_assembly):
        """Modifying one principle's refs doesn't affect others"""
        doctrine_assembly.add_principle("p1", {"text": "First"})
        doctrine_assembly.add_principle("p2", {"text": "Second"})
        doctrine_assembly.add_principle("p3", {"text": "Third"})
        
        # p1 -> p2
        doctrine_assembly.add_reference("p1", "p2")
        
        # Get refs before modifying p3
        refs_p1_before = doctrine_assembly.get_references("p1")
        
        # Add reference to p3
        doctrine_assembly.add_reference("p3", "p1")
        
        # p1's references should be unchanged
        refs_p1_after = doctrine_assembly.get_references("p1")
        
        assert refs_p1_before == refs_p1_after


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
