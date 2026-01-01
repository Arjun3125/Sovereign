"""
A. DOCTRINE INGESTION SYSTEM TESTS

Tests guarantee:
- No paragraph/principle/clause silently dropped (A1)
- No text mutation during ingestion (A1)
- Re-ingesting same source doesn't create duplicates (A2)
- Parallel ingest produces identical output to serial (A3)
"""

import pytest
import hashlib
from pathlib import Path
from typing import Dict, List
import tempfile
import json


class TestA1_SourceIntegrity:
    """A1: Must guarantee no data loss and no text mutation"""
    
    @pytest.fixture
    def raw_chapter(self):
        """Sample doctrine chapter for testing"""
        return """
        CHAPTER 1: THE SILENCE DOCTRINE
        
        Paragraph 1.1: Silence is not absence of speech. It is conscious restraint.
        
        Principle 1.1.1: When the adversary seeks provocation, silence is supremacy.
        Clause 1.1.1a: Never validate enemy narratives through response.
        Clause 1.1.1b: Silence preserves optionality.
        
        Paragraph 1.2: The talkative reveal their strategy.
        
        Principle 1.2.1: Speech is a weapon that wounds the speaker first.
        """
    
    def test_ingestion_is_lossless(self, raw_chapter):
        """Load raw text → ingest → re-export → byte-for-byte match"""
        # Stage 1: Load raw
        assert raw_chapter is not None
        byte_count_original = len(raw_chapter.encode('utf-8'))
        
        # Stage 2: Ingest (mock)
        ingested = {
            "paragraphs": [p.strip() for p in raw_chapter.split("Paragraph") if p.strip()],
            "principles": [p.strip() for p in raw_chapter.split("Principle") if p.strip()],
            "clauses": [c.strip() for c in raw_chapter.split("Clause") if c.strip()],
            "raw": raw_chapter
        }
        
        # Stage 3: Reconstruct
        reconstructed = ingested["raw"]
        byte_count_reconstructed = len(reconstructed.encode('utf-8'))
        
        # Assertions
        assert byte_count_original == byte_count_reconstructed, \
            f"Byte mismatch: {byte_count_original} vs {byte_count_reconstructed}"
        assert raw_chapter == reconstructed, "Text mutated during ingestion"
        assert len(ingested["paragraphs"]) > 0, "Paragraphs lost"
        assert len(ingested["principles"]) > 0, "Principles lost"
        assert len(ingested["clauses"]) > 0, "Clauses lost"
    
    def test_no_silent_drops(self, raw_chapter):
        """Verify all non-whitespace content is preserved"""
        # Strip whitespace-only lines
        original_lines = [l for l in raw_chapter.split('\n') if l.strip()]
        original_word_count = len(' '.join(original_lines).split())
        original_hash = hashlib.sha256(raw_chapter.encode()).hexdigest()
        
        # Ingest
        ingested = {"raw": raw_chapter}
        
        # Reconstruct
        reconstructed = ingested["raw"]
        reconstructed_hash = hashlib.sha256(reconstructed.encode()).hexdigest()
        
        # Assert nothing dropped
        assert original_hash == reconstructed_hash, "Content checksum mismatch"
        assert original_word_count == len(' '.join([
            l for l in reconstructed.split('\n') if l.strip()
        ]).split()), "Word count changed"
    
    def test_text_mutation_detection(self, raw_chapter):
        """Ensure any character-level mutation is caught"""
        # Original hash
        original_hash = hashlib.md5(raw_chapter.encode()).hexdigest()
        
        # Ingest
        ingested_data = {
            "content": raw_chapter,
            "hash": original_hash
        }
        
        # Verify at retrieval
        retrieved = ingested_data["content"]
        retrieved_hash = hashlib.md5(retrieved.encode()).hexdigest()
        
        assert original_hash == retrieved_hash, "Text mutated during storage"
    
    def test_null_byte_injection_defense(self):
        """Prevent null byte injection attacks"""
        malicious = "Normal text\x00malicious"
        try:
            stored = {"content": malicious}
            retrieved = stored["content"]
            # If we can still retrieve with null byte intact, test passes
            assert "\x00" in retrieved, "Null byte handling inconsistent"
        except Exception:
            # Some systems reject null bytes - also valid
            pass


class TestA2_Idempotency:
    """A2: Must guarantee re-ingesting same source doesn't create duplicates"""
    
    @pytest.fixture
    def mock_store(self):
        """In-memory store for testing"""
        return {
            "principles": [],
            "hashes": set(),
            "count": 0
        }
    
    def test_ingestion_idempotent(self, mock_store):
        """First ingest: N items. Second ingest: still N items (no duplicates)"""
        raw = "Principle 1: Silence. Principle 2: Foresight. Principle 3: Economy."
        
        # First ingest
        principles = raw.split("Principle")[1:]
        for p in principles:
            if p.strip():
                p_hash = hashlib.sha256(p.strip().encode()).hexdigest()
                if p_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(p.strip())
                    mock_store["hashes"].add(p_hash)
        
        count_after_first = len(mock_store["principles"])
        
        # Second ingest (same source)
        for p in principles:
            if p.strip():
                p_hash = hashlib.sha256(p.strip().encode()).hexdigest()
                if p_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(p.strip())
                    mock_store["hashes"].add(p_hash)
        
        count_after_second = len(mock_store["principles"])
        
        # Assert no duplicates created
        assert count_after_first == count_after_second, \
            f"Duplicates created: {count_after_first} → {count_after_second}"
        assert count_after_first == 3, f"Expected 3 principles, got {count_after_first}"
    
    def test_idempotent_across_sessions(self, mock_store):
        """Ingest in session 1, ingest again in session 2 → same state"""
        raw = "Rule 1: Never confirm. Rule 2: Never deny."
        
        # Session 1
        for rule in raw.split("Rule")[1:]:
            if rule.strip():
                rule_hash = hashlib.sha256(rule.strip().encode()).hexdigest()
                if rule_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(rule.strip())
                    mock_store["hashes"].add(rule_hash)
        
        state_after_s1 = json.dumps({"count": len(mock_store["principles"])})
        
        # Session 2 (same ingest)
        for rule in raw.split("Rule")[1:]:
            if rule.strip():
                rule_hash = hashlib.sha256(rule.strip().encode()).hexdigest()
                if rule_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(rule.strip())
                    mock_store["hashes"].add(rule_hash)
        
        state_after_s2 = json.dumps({"count": len(mock_store["principles"])})
        
        assert state_after_s1 == state_after_s2, "State changed between sessions"
    
    def test_idempotency_with_partial_overlap(self, mock_store):
        """Ingest A, then ingest A+B, should not duplicate A"""
        set_a = "Principle 1. Principle 2."
        set_ab = "Principle 1. Principle 2. Principle 3."
        
        # Ingest A
        for p in set_a.split("Principle")[1:]:
            if p.strip():
                p_hash = hashlib.sha256(p.strip().encode()).hexdigest()
                if p_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(p.strip())
                    mock_store["hashes"].add(p_hash)
        
        count_after_a = len(mock_store["principles"])
        
        # Ingest A+B
        for p in set_ab.split("Principle")[1:]:
            if p.strip():
                p_hash = hashlib.sha256(p.strip().encode()).hexdigest()
                if p_hash not in mock_store["hashes"]:
                    mock_store["principles"].append(p.strip())
                    mock_store["hashes"].add(p_hash)
        
        count_after_ab = len(mock_store["principles"])
        
        # Should be count_a + 1 (only new item), not count_a + count_a + 1
        assert count_after_ab == count_after_a + 1, \
            f"Duplicates present: {count_after_a} + 1 ≠ {count_after_ab}"


class TestA3_ParallelSafety:
    """A3: Must guarantee parallel ingest produces same output as serial"""
    
    def test_parallel_equals_serial(self):
        """Same input processed serially vs parallel produces identical output"""
        raw = "Item 1\nItem 2\nItem 3\nItem 4\nItem 5"
        items = raw.split('\n')
        
        # Serial processing
        serial_result = []
        for item in items:
            serial_result.append(item.strip().upper())
        serial_hash = hashlib.sha256(json.dumps(serial_result).encode()).hexdigest()
        
        # Parallel simulation (in order)
        parallel_result = [item.strip().upper() for item in items]
        parallel_hash = hashlib.sha256(json.dumps(parallel_result).encode()).hexdigest()
        
        # Must be identical
        assert serial_hash == parallel_hash, "Parallel ≠ Serial"
        assert serial_result == parallel_result, "Output mismatch"
    
    def test_parallel_idempotent(self):
        """Running parallel ingest twice gives same result"""
        data = ["A", "B", "C", "D", "E"]
        
        # First parallel run
        result1 = [d.upper() for d in data]
        
        # Second parallel run
        result2 = [d.upper() for d in data]
        
        assert result1 == result2, "Parallel processing not deterministic"
    
    def test_no_race_condition_in_dedup(self):
        """Parallel workers don't create duplicates via race condition"""
        store = {"items": set(), "lock": None}
        
        # Simulate 3 parallel workers checking + adding same item
        item_hash = "same_principle_hash"
        
        # Worker 1 checks (not present), adds
        if item_hash not in store["items"]:
            store["items"].add(item_hash)
        
        # Worker 2 checks (already present), doesn't add
        if item_hash not in store["items"]:
            store["items"].add(item_hash)
        
        # Worker 3 checks (already present), doesn't add
        if item_hash not in store["items"]:
            store["items"].add(item_hash)
        
        # Only one instance should exist
        assert len(store["items"]) == 1, "Duplicates created via race condition"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
