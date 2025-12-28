
import unittest
import os
import shutil
import time
from pathlib import Path
from core.memory.memory_store import MemoryStore
from core.memory.override_tracker import OverrideRecord
from core.memory.event_log import MemoryEvent

class TestMemoryStoreOverrides(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for the database
        self.test_db_dir = Path("tests/data/memory")
        self.test_db_path = self.test_db_dir / "cold_strategist.db"

        # Clean up any existing test DB
        if self.test_db_dir.exists():
            shutil.rmtree(self.test_db_dir)

        # Mock the DB path in Database class or MemoryStore
        from core.memory.database import Database
        self.original_db_dir = Database.DB_DIR
        self.original_db_path = Database.DB_PATH
        self.original_schema_path = Database.SCHEMA_PATH

        Database.DB_DIR = self.test_db_dir
        Database.DB_PATH = self.test_db_path
        Database.SCHEMA_PATH = self.test_db_dir / "schema.sql"

        self.store = MemoryStore()

    def tearDown(self):
        # Restore constants
        from core.memory.database import Database
        Database.DB_DIR = self.original_db_dir
        Database.DB_PATH = self.original_db_path
        Database.SCHEMA_PATH = self.original_schema_path

        # Clean up files
        if self.test_db_dir.exists():
            shutil.rmtree(self.test_db_dir)

    def test_load_overrides(self):
        # 1. Verify initially empty
        overrides = self.store.load_overrides()
        self.assertEqual(overrides, [], "Should be empty initially")

        # 2. Add events first (required for FK constraint)
        event1 = MemoryEvent(
            event_id="evt_1",
            timestamp=time.time(),
            session_index=1,
            domain="diplomacy",
            stakes="high",
            emotional_load="medium",
            ministers_called=["M1"],
            verdict_position="attack",
            verdict_posture="aggressive",
            illusions_detected=[],
            contradictions_found=0,
            sovereign_decision="attack",
            action_followed_counsel=True
        )
        self.store.save_event(event1)

        event2 = MemoryEvent(
            event_id="evt_2",
            timestamp=time.time(),
            session_index=1,
            domain="economy",
            stakes="medium",
            emotional_load="low",
            ministers_called=["M2"],
            verdict_position="save",
            verdict_posture="conservative",
            illusions_detected=[],
            contradictions_found=0,
            sovereign_decision="spend",
            action_followed_counsel=False
        )
        self.store.save_event(event2)

        # 3. Add some overrides
        override1 = OverrideRecord(
            event_id="evt_1",
            domain="diplomacy",
            counsel_posture="caution",
            actual_action="attack",
            override_reason="strategic surprise"
        )

        override2 = OverrideRecord(
            event_id="evt_2",
            domain="economy",
            counsel_posture="save",
            actual_action="spend",
            override_reason="stimulus"
        )

        self.store.save_override(override1)
        self.store.save_override(override2)

        # 4. Load overrides and verify
        loaded_overrides = self.store.load_overrides()

        # Note: Current implementation returns empty list, so this test is expected to FAIL
        self.assertEqual(len(loaded_overrides), 2)

        # Sort by event_id for consistent comparison
        loaded_overrides.sort(key=lambda x: x.event_id)

        self.assertEqual(loaded_overrides[0].event_id, "evt_1")
        self.assertEqual(loaded_overrides[0].domain, "diplomacy")
        self.assertEqual(loaded_overrides[0].counsel_posture, "caution")
        self.assertEqual(loaded_overrides[0].actual_action, "attack")
        self.assertEqual(loaded_overrides[0].override_reason, "strategic surprise")

        self.assertEqual(loaded_overrides[1].event_id, "evt_2")
        self.assertEqual(loaded_overrides[1].domain, "economy")

if __name__ == "__main__":
    unittest.main()
