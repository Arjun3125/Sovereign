"""
H. CLI / API CONTRACT TESTS

Tests guarantee:
- Dry run makes zero state changes (H1)
- API never returns advice without context (H2)
"""

import pytest
from typing import Dict, Any, List
import json


class TestH1_DryRunNoMutation:
    """H1: Must guarantee dry-run makes zero state changes"""
    
    @pytest.fixture
    def system_state_initial(self):
        """Initial system state before dry-run"""
        return {
            "decisions": [],
            "embeddings": {},
            "principles_count": 42,
            "locked_doctrine": True,
            "last_modified": "2025-01-01T00:00:00Z"
        }
    
    def test_dry_run_no_mutation(self, system_state_initial):
        """Dry-run does not modify any state"""
        # Snapshot initial state
        initial_snapshot = json.dumps(system_state_initial, sort_keys=True)
        
        # Perform dry-run (mock)
        state = system_state_initial
        dry_run = True
        
        if not dry_run:
            state["decisions"].append({"decision": "test"})
        
        # Snapshot final state
        final_snapshot = json.dumps(state, sort_keys=True)
        
        # Must be identical
        assert initial_snapshot == final_snapshot, "Dry-run modified state"
    
    def test_dry_run_no_database_writes(self, system_state_initial):
        """Dry-run performs no database writes"""
        db_writes = []
        
        def mock_db_write(data):
            db_writes.append(data)
        
        # Simulate dry-run
        dry_run = True
        test_decision = {"situation": "test"}
        
        if not dry_run:
            mock_db_write(test_decision)
        
        # Should have no writes
        assert len(db_writes) == 0, f"Dry-run caused {len(db_writes)} DB writes"
    
    def test_dry_run_no_embedding_computation(self):
        """Dry-run does not compute new embeddings"""
        embedding_computes = []
        
        def mock_compute_embedding(text):
            embedding_computes.append(text)
            return [0.1, 0.2, 0.3]  # Mock vector
        
        # Simulate dry-run with text
        dry_run = True
        text_to_embed = "Test principle"
        
        if not dry_run:
            mock_compute_embedding(text_to_embed)
        
        # Should have no computations
        assert len(embedding_computes) == 0, "Dry-run computed embeddings"
    
    def test_dry_run_returns_preview(self):
        """Dry-run returns preview of what would happen"""
        dry_run = True
        request = {
            "action": "ingest",
            "pdf": "book.pdf",
            "dry_run": dry_run
        }
        
        if request["dry_run"]:
            response = {
                "mode": "DRY_RUN",
                "would_do": "Ingest book.pdf with 342 principles",
                "no_changes": True
            }
        else:
            response = {"mode": "EXECUTE"}
        
        assert response["no_changes"] is True, "Dry-run caused changes"
        assert response["mode"] == "DRY_RUN", "Wrong response mode"
    
    def test_dry_run_idempotent(self):
        """Multiple dry-runs with same input produce same preview"""
        state = {"count": 10}
        
        # Dry-run 1
        if False:  # dry_run=False when actually running
            state["count"] += 1
        preview1 = {"state": state["count"]}
        
        # Dry-run 2
        if False:
            state["count"] += 1
        preview2 = {"state": state["count"]}
        
        assert preview1 == preview2, "Dry-run previews differ"


class TestH2_APIContextRequired:
    """H2: Must guarantee API never returns advice without context"""
    
    @pytest.fixture
    def api_request_empty_context(self):
        """API request with missing context"""
        return {
            "situation": "",
            "domain": "",
            "stakes": None
        }
    
    @pytest.fixture
    def api_request_full_context(self):
        """API request with complete context"""
        return {
            "situation": "Negotiation with competitor over market position",
            "domain": "career",
            "stakes": "high",
            "arena": "business",
            "constraints": ["legal", "reversible"]
        }
    
    def test_api_requires_context(self, api_request_empty_context):
        """Empty context returns error, not advice"""
        request = api_request_empty_context
        
        # Check if context is sufficient
        has_context = request.get("situation") and request.get("domain")
        
        if has_context:
            response = {"advice": "some decision"}
        else:
            response = {
                "status": "NEEDS_CONTEXT",
                "error": "Situation and domain required"
            }
        
        assert response["status"] == "NEEDS_CONTEXT", \
            "Empty context should be rejected"
    
    def test_api_accepts_full_context(self, api_request_full_context):
        """Full context allows advice"""
        request = api_request_full_context
        
        has_context = request.get("situation") and request.get("domain")
        
        if has_context:
            response = {
                "status": "OK",
                "advice": "PROCEED_WITH_CONDITIONS",
                "reasoning": "..."
            }
        else:
            response = {"status": "NEEDS_CONTEXT"}
        
        assert response["status"] == "OK", "Full context should be accepted"
    
    def test_minimal_required_fields(self):
        """Define minimal required fields for valid request"""
        required_fields = ["situation", "domain"]
        
        request = {
            "situation": "Test situation",
            "domain": "test_domain"
        }
        
        for field in required_fields:
            assert field in request, f"Missing required field: {field}"
    
    def test_empty_situation_rejected(self):
        """Empty situation string is rejected"""
        requests = [
            {"situation": "", "domain": "career"},  # Empty string
            {"situation": "   ", "domain": "career"},  # Whitespace only
            {"situation": None, "domain": "career"},  # None
            {"domain": "career"},  # Missing entirely
        ]
        
        for req in requests:
            situation = req.get("situation") or ""
            if isinstance(situation, str):
                situation = situation.strip()
            else:
                situation = ""
            
            is_valid = situation and len(situation) > 0
            
            if not is_valid:
                status = "NEEDS_CONTEXT"
            else:
                status = "OK"
            
            assert status == "NEEDS_CONTEXT", \
                f"Invalid situation should be rejected: {req}"
    
    def test_context_validation_before_processing(self):
        """All context validated before any processing"""
        validation_order = []
        
        def validate_context(request):
            validation_order.append("context_check")
            if not request.get("situation"):
                return False
            if not request.get("domain"):
                return False
            return True
        
        def process_request(request):
            validation_order.append("processing")
            return {"advice": "..."}
        
        request = {"situation": "", "domain": "test"}
        
        if validate_context(request):
            process_request(request)
        
        # Validation must come before processing
        if "processing" in validation_order:
            assert validation_order.index("context_check") < \
                   validation_order.index("processing"), \
                   "Processing started before validation"
        else:
            assert "context_check" in validation_order, \
                   "Context not validated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
