"""
Database Layer - SQLite Connection and Initialization (LOCKED)

Production-grade persistence for memory layer.

Local-first. ACID. Deterministic. No infra tax.

Tables:
- events: Immutable ledger (INSERT-only)
- outcomes: Delayed resolution
- patterns: Derived signal
- minister_calibration: Credibility tracking
- overrides: Counsel ignored log
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime


class Database:
    """
    SQLite database connection and query interface.
    
    Guarantees:
    - ACID transactions
    - Immutable event log
    - Queryable outcomes and patterns
    - Zero doctrine mutation
    """
    
    # Database location
    DB_DIR = Path("data/memory")
    DB_PATH = DB_DIR / "cold_strategist.db"
    SCHEMA_PATH = DB_DIR / "schema.sql"
    
    def __init__(self):
        """Initialize database connection."""
        self.db_dir = self.DB_DIR
        self.db_path = self.DB_PATH
        
        # Create directory if needed
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema on first run
        self._init_schema()
    
    def _init_schema(self) -> None:
        """
        Initialize database schema if not exists.
        
        Reads from schema.sql and executes all statements.
        """
        # Check if database is already initialized
        if self.db_path.exists():
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
                )
                if cursor.fetchone():
                    return  # Already initialized
        
        # Read and execute schema
        if self.SCHEMA_PATH.exists():
            with open(self.SCHEMA_PATH, "r") as f:
                schema_sql = f.read()
        else:
            # Fallback: create schema inline
            schema_sql = self._get_default_schema()
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get SQLite connection with proper settings.
        
        Returns:
            sqlite3.Connection
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def execute(
        self,
        sql: str,
        params: tuple = ()
    ) -> sqlite3.Cursor:
        """
        Execute query and return cursor.
        
        Args:
            sql: SQL query
            params: Query parameters
            
        Returns:
            Cursor with results
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor
    
    def execute_write(
        self,
        sql: str,
        params: tuple = ()
    ) -> None:
        """
        Execute write operation (INSERT/UPDATE/DELETE).
        
        Args:
            sql: SQL query
            params: Query parameters
        """
        conn = self.get_connection()
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()
    
    def fetchall(
        self,
        sql: str,
        params: tuple = ()
    ) -> List[sqlite3.Row]:
        """
        Fetch all results.
        
        Args:
            sql: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def fetchone(
        self,
        sql: str,
        params: tuple = ()
    ) -> Optional[sqlite3.Row]:
        """
        Fetch single result.
        
        Args:
            sql: SQL query
            params: Query parameters
            
        Returns:
            Single row or None
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    # ========================================================================
    # EVENT OPERATIONS
    # ========================================================================
    
    def insert_event(
        self,
        event_id: str,
        timestamp: int,
        session_index: int,
        domain: str,
        stakes: str,
        emotional_load: float,
        urgency: float,
        ministers_called: List[str],
        verdict: str,
        posture: str,
        illusions_detected: List[str],
        contradictions_found: int,
        sovereign_action: str,
        action_followed_counsel: bool,
        override_reason: Optional[str] = None
    ) -> None:
        """
        Insert event into ledger (INSERT-only).
        
        Args:
            event_id: Unique event ID
            timestamp: Unix timestamp
            session_index: Sequential session number
            domain: Decision domain
            stakes: Stakes level
            emotional_load: 0-1 emotional intensity
            urgency: 0-1 urgency level
            ministers_called: List of minister names
            verdict: N's verdict
            posture: N's posture
            illusions_detected: List of illusions flagged
            contradictions_found: Count of contradictions
            sovereign_action: What human did
            action_followed_counsel: Whether it matched posture
            override_reason: Why overridden (if applicable)
        """
        self.execute_write("""
            INSERT INTO events (
                id, timestamp, session_index, domain, stakes, emotional_load, urgency,
                ministers_called, verdict, posture, illusions_detected, contradictions_found,
                sovereign_action, action_followed_counsel, override_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp,
            session_index,
            domain,
            stakes,
            emotional_load,
            urgency,
            json.dumps(ministers_called),
            verdict,
            posture,
            json.dumps(illusions_detected),
            contradictions_found,
            sovereign_action,
            1 if action_followed_counsel else 0,
            override_reason
        ))
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """Get single event by ID."""
        row = self.fetchone("SELECT * FROM events WHERE id = ?", (event_id,))
        return dict(row) if row else None
    
    def get_all_events(self) -> List[Dict]:
        """Get all events in chronological order."""
        rows = self.fetchall(
            "SELECT * FROM events ORDER BY timestamp ASC"
        )
        return [dict(row) for row in rows]
    
    def get_events_by_domain(self, domain: str) -> List[Dict]:
        """Get all events in specific domain."""
        rows = self.fetchall(
            "SELECT * FROM events WHERE domain = ? ORDER BY timestamp ASC",
            (domain,)
        )
        return [dict(row) for row in rows]
    
    def get_unresolved_events(self) -> List[Dict]:
        """Get events without outcomes."""
        rows = self.fetchall("""
            SELECT e.* FROM events e
            LEFT JOIN outcomes o ON e.id = o.event_id
            WHERE o.event_id IS NULL
            ORDER BY e.timestamp ASC
        """)
        return [dict(row) for row in rows]
    
    # ========================================================================
    # OUTCOME OPERATIONS
    # ========================================================================
    
    def insert_outcome(
        self,
        event_id: str,
        resolved_at: int,
        result: str,
        damage: float,
        benefit: float,
        lessons: List[str]
    ) -> None:
        """
        Insert outcome for event (delayed resolution).
        
        Args:
            event_id: ID of event being resolved
            resolved_at: Unix timestamp of resolution
            result: "success" | "partial" | "failure"
            damage: 0-1 scale of damage
            benefit: 0-1 scale of benefit
            lessons: List of lessons learned
        """
        self.execute_write("""
            INSERT OR REPLACE INTO outcomes (
                event_id, resolved_at, result, damage, benefit, lessons
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            resolved_at,
            result,
            damage,
            benefit,
            json.dumps(lessons)
        ))
    
    def get_outcome(self, event_id: str) -> Optional[Dict]:
        """Get outcome for event."""
        row = self.fetchone("SELECT * FROM outcomes WHERE event_id = ?", (event_id,))
        return dict(row) if row else None
    
    def get_outcomes_by_result(self, result: str) -> List[Dict]:
        """Get all outcomes with specific result."""
        rows = self.fetchall(
            "SELECT * FROM outcomes WHERE result = ?",
            (result,)
        )
        return [dict(row) for row in rows]
    
    # ========================================================================
    # PATTERN OPERATIONS
    # ========================================================================
    
    def insert_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        domain: Optional[str],
        illusion_type: Optional[str],
        frequency: int,
        last_seen: Optional[int],
        last_outcome: Optional[str]
    ) -> None:
        """
        Insert detected pattern.
        
        Args:
            pattern_id: Unique pattern ID
            pattern_type: Type of pattern
            description: Human-readable description
            domain: Associated domain (if any)
            illusion_type: Associated illusion (if any)
            frequency: How many times seen
            last_seen: Last timestamp seen
            last_outcome: Last outcome of this pattern
        """
        self.execute_write("""
            INSERT OR REPLACE INTO patterns (
                id, pattern_type, description, domain, illusion_type,
                frequency, last_seen, last_outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id,
            pattern_type,
            description,
            domain,
            illusion_type,
            frequency,
            last_seen,
            last_outcome
        ))
    
    def get_patterns(self) -> List[Dict]:
        """Get all detected patterns."""
        rows = self.fetchall("SELECT * FROM patterns ORDER BY frequency DESC")
        return [dict(row) for row in rows]
    
    def get_patterns_by_domain(self, domain: str) -> List[Dict]:
        """Get patterns in specific domain."""
        rows = self.fetchall(
            "SELECT * FROM patterns WHERE domain = ? ORDER BY frequency DESC",
            (domain,)
        )
        return [dict(row) for row in rows]
    
    # ========================================================================
    # CALIBRATION OPERATIONS
    # ========================================================================
    
    def set_calibration(
        self,
        minister: str,
        domain: str,
        confidence: float
    ) -> None:
        """
        Set minister calibration for domain.
        
        Args:
            minister: Minister name
            domain: Decision domain
            confidence: Confidence score (0.0-1.0)
        """
        self.execute_write("""
            INSERT OR REPLACE INTO minister_calibration (
                minister, domain, confidence, updated_at
            ) VALUES (?, ?, ?, datetime('now'))
        """, (minister, domain, confidence))
    
    def get_calibration(self, minister: str, domain: str) -> float:
        """Get minister calibration for domain."""
        row = self.fetchone(
            "SELECT confidence FROM minister_calibration WHERE minister = ? AND domain = ?",
            (minister, domain)
        )
        return row["confidence"] if row else 0.5
    
    def get_all_calibrations(self) -> Dict[str, Dict[str, float]]:
        """Get all minister calibrations."""
        rows = self.fetchall("SELECT * FROM minister_calibration")
        result = {}
        for row in rows:
            minister = row["minister"]
            if minister not in result:
                result[minister] = {}
            result[minister][row["domain"]] = row["confidence"]
        return result
    
    # ========================================================================
    # OVERRIDE OPERATIONS
    # ========================================================================
    
    def insert_override(
        self,
        override_id: str,
        event_id: str,
        domain: str,
        counsel_posture: str,
        actual_action: str,
        override_reason: Optional[str]
    ) -> None:
        """
        Insert override record.
        
        Args:
            override_id: Unique override ID
            event_id: Associated event ID
            domain: Decision domain
            counsel_posture: What was recommended
            actual_action: What human did
            override_reason: Why overridden
        """
        self.execute_write("""
            INSERT INTO overrides (
                id, event_id, domain, counsel_posture, actual_action, override_reason
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            override_id,
            event_id,
            domain,
            counsel_posture,
            actual_action,
            override_reason
        ))
    
    def get_all_overrides(self) -> List[Dict]:
        """Get all overrides."""
        rows = self.fetchall(
            "SELECT * FROM overrides ORDER BY created_at ASC"
        )
        return [dict(row) for row in rows]

    def get_overrides_by_domain(self, domain: str) -> List[Dict]:
        """Get all overrides in domain."""
        rows = self.fetchall(
            "SELECT * FROM overrides WHERE domain = ? ORDER BY created_at DESC",
            (domain,)
        )
        return [dict(row) for row in rows]
    
    def get_failed_overrides(self) -> List[Dict]:
        """Get overrides that failed."""
        rows = self.fetchall(
            "SELECT * FROM overrides WHERE outcome_result = 'failure'"
        )
        return [dict(row) for row in rows]
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def stats(self) -> Dict:
        """Get database statistics."""
        event_count = self.fetchone("SELECT COUNT(*) as count FROM events")["count"]
        outcome_count = self.fetchone("SELECT COUNT(*) as count FROM outcomes")["count"]
        pattern_count = self.fetchone("SELECT COUNT(*) as count FROM patterns")["count"]
        override_count = self.fetchone("SELECT COUNT(*) as count FROM overrides")["count"]
        
        return {
            "events": event_count,
            "outcomes": outcome_count,
            "patterns": pattern_count,
            "overrides": override_count
        }
    
    def _get_default_schema(self) -> str:
        """Fallback schema if file not found."""
        return """
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            session_index INTEGER,
            domain TEXT NOT NULL,
            stakes TEXT,
            emotional_load REAL,
            urgency REAL,
            ministers_called TEXT NOT NULL,
            verdict TEXT NOT NULL,
            posture TEXT NOT NULL,
            illusions_detected TEXT,
            contradictions_found INTEGER,
            sovereign_action TEXT NOT NULL,
            action_followed_counsel INTEGER,
            override_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS outcomes (
            event_id TEXT PRIMARY KEY,
            resolved_at INTEGER NOT NULL,
            result TEXT NOT NULL,
            damage REAL NOT NULL,
            benefit REAL NOT NULL,
            lessons TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            pattern_type TEXT NOT NULL,
            description TEXT NOT NULL,
            domain TEXT,
            illusion_type TEXT,
            frequency INTEGER NOT NULL,
            last_seen INTEGER,
            last_outcome TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            rebuilt_at INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS minister_calibration (
            minister TEXT NOT NULL,
            domain TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(minister, domain)
        );
        
        CREATE TABLE IF NOT EXISTS overrides (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            domain TEXT NOT NULL,
            counsel_posture TEXT NOT NULL,
            actual_action TEXT NOT NULL,
            override_reason TEXT,
            outcome_result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
