"""
I1. PARTIAL INGEST RECOVERY TEST

Test guarantees:
- Ingestion crash mid-process doesn't corrupt data
- Partial ingests can be recovered/continued
- Transaction atomicity (all-or-nothing commits)
- No zombie records from failed ingests
"""

import pytest
from typing import Dict, List, Any


class TestI1_PartialIngestRecovery:
    """I1: Must guarantee recovery from partial ingestion"""
    
    @pytest.fixture
    def ingest_system(self):
        """Mock ingest system with transaction support"""
        class IngestSystem:
            def __init__(self):
                self.committed = []
                self.staging = []
                self.recovery_log = []
            
            def start_transaction(self, batch_id: str) -> Dict:
                """Begin atomic transaction"""
                return {
                    "batch_id": batch_id,
                    "status": "started",
                    "in_progress": True
                }
            
            def add_to_staging(self, item: Dict, batch_id: str) -> bool:
                """Add item to staging (not committed)"""
                self.staging.append({
                    "batch_id": batch_id,
                    "item": item
                })
                return True
            
            def commit_transaction(self, batch_id: str) -> bool:
                """Atomically commit all items or none"""
                batch_items = [s for s in self.staging if s["batch_id"] == batch_id]
                
                if not batch_items:
                    return False
                
                # All or nothing
                for s in batch_items:
                    self.committed.append(s["item"])
                
                # Remove from staging
                self.staging = [s for s in self.staging if s["batch_id"] != batch_id]
                
                return True
            
            def rollback_transaction(self, batch_id: str) -> bool:
                """Rollback all items in batch"""
                self.staging = [s for s in self.staging if s["batch_id"] != batch_id]
                self.recovery_log.append({
                    "batch_id": batch_id,
                    "action": "rollback"
                })
                return True
            
            def ingest_batch(self, items: List[Dict], batch_id: str, should_crash: bool = False) -> Dict:
                """Ingest batch - can crash mid-way"""
                self.start_transaction(batch_id)
                
                for i, item in enumerate(items):
                    if should_crash and i == len(items) // 2:
                        # Crash mid-way
                        self.rollback_transaction(batch_id)
                        return {
                            "status": "crashed",
                            "batch_id": batch_id,
                            "processed": i,
                            "committed": 0
                        }
                    
                    self.add_to_staging(item, batch_id)
                
                # Successful completion
                success = self.commit_transaction(batch_id)
                return {
                    "status": "committed" if success else "failed",
                    "batch_id": batch_id,
                    "committed": len([i for i in self.committed if True])
                }
        
        return IngestSystem()
    
    def test_successful_ingest_commits(self, ingest_system):
        """Successful ingest commits all items"""
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        
        result = ingest_system.ingest_batch(items, "batch_1")
        
        assert result["status"] == "committed"
        assert len(ingest_system.committed) == 3
    
    def test_crash_doesnt_corrupt(self, ingest_system):
        """Crash mid-ingest doesn't corrupt committed data"""
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        
        result = ingest_system.ingest_batch(items, "crash_batch", should_crash=True)
        
        assert result["status"] == "crashed"
        assert len(ingest_system.committed) == 0  # No corruption
    
    def test_staging_cleared_on_rollback(self, ingest_system):
        """Rollback clears staging completely"""
        ingest_system.add_to_staging({"id": "1"}, "batch_1")
        ingest_system.add_to_staging({"id": "2"}, "batch_1")
        
        assert len(ingest_system.staging) == 2
        
        ingest_system.rollback_transaction("batch_1")
        
        assert len(ingest_system.staging) == 0
    
    def test_partial_ingest_not_visible(self, ingest_system):
        """Partial ingest items not visible in committed data"""
        items = [{"id": str(i)} for i in range(10)]
        
        ingest_system.ingest_batch(items, "partial", should_crash=True)
        
        # No items should be visible
        assert len(ingest_system.committed) == 0
    
    def test_rollback_logged(self, ingest_system):
        """Rollback is logged for recovery"""
        ingest_system.start_transaction("batch_1")
        ingest_system.add_to_staging({"id": "test"}, "batch_1")
        ingest_system.rollback_transaction("batch_1")
        
        assert len(ingest_system.recovery_log) == 1
        assert ingest_system.recovery_log[0]["batch_id"] == "batch_1"
    
    def test_atomicity_multiple_batches(self, ingest_system):
        """Multiple batches independently atomic"""
        items1 = [{"id": "1"}]
        items2 = [{"id": "2"}]
        
        ingest_system.ingest_batch(items1, "b1")
        ingest_system.ingest_batch(items2, "b2", should_crash=True)
        
        # b1 committed, b2 rolled back
        assert len(ingest_system.committed) == 1
    
    def test_no_zombie_records(self, ingest_system):
        """No partial/zombie records survive ingest failure"""
        items = [{"id": f"item_{i}"} for i in range(20)]
        
        ingest_system.ingest_batch(items, "zombie_test", should_crash=True)
        
        # All or nothing
        assert len(ingest_system.committed) == 0
    
    def test_recovery_possible_after_crash(self, ingest_system):
        """System can recover after crash"""
        items = [{"id": "retry"}]
        
        # First attempt crashes
        r1 = ingest_system.ingest_batch(items, "retry_1", should_crash=True)
        assert r1["status"] == "crashed"
        
        # Retry succeeds
        r2 = ingest_system.ingest_batch(items, "retry_2")
        assert r2["status"] == "committed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
