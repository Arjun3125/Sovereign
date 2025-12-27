-- Memory Persistence Schema (LOCKED v1)
-- 
-- Immutable event log with delayed outcomes.
-- Queryable patterns. Calibration over time.
-- Zero doctrine mutation.
--
-- Rule: events table is INSERT-only. Never UPDATE.

-- ============================================================================
-- EVENTS — Immutable Ledger
-- ============================================================================
-- Every Darbar session writes one row. Never updated.
-- Ground truth for all analysis.

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    session_index INTEGER,
    
    -- Context at decision time
    domain TEXT NOT NULL,
    stakes TEXT,
    emotional_load REAL,
    urgency REAL,
    
    -- Execution
    ministers_called TEXT NOT NULL,  -- JSON list of minister names
    verdict TEXT NOT NULL,           -- What N recommended
    posture TEXT NOT NULL,           -- abort | force | delay | conditional
    
    -- Intelligence
    illusions_detected TEXT,         -- JSON list
    contradictions_found INTEGER,
    
    -- Sovereign action
    sovereign_action TEXT NOT NULL,  -- What human did
    action_followed_counsel INTEGER, -- 1 = followed, 0 = ignored
    override_reason TEXT,
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_domain ON events(domain);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_index);


-- ============================================================================
-- OUTCOMES — Delayed Resolution
-- ============================================================================
-- Inserted days/weeks after decision.
-- Enables accurate consequence assessment.

CREATE TABLE IF NOT EXISTS outcomes (
    event_id TEXT PRIMARY KEY,
    
    -- Resolution
    resolved_at INTEGER NOT NULL,
    result TEXT NOT NULL,            -- success | partial | failure
    
    -- Impact
    damage REAL NOT NULL,            -- 0-1 scale
    benefit REAL NOT NULL,           -- 0-1 scale
    lessons TEXT,                    -- JSON list
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(event_id) REFERENCES events(id)
);

CREATE INDEX IF NOT EXISTS idx_outcomes_result ON outcomes(result);


-- ============================================================================
-- PATTERNS — Derived Signal
-- ============================================================================
-- Detected from events. Rebuilt on demand.
-- Never treated as truth — only signal.

CREATE TABLE IF NOT EXISTS patterns (
    id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,      -- repetition_loop | override_loop | etc
    
    -- Pattern description
    description TEXT NOT NULL,
    domain TEXT,
    illusion_type TEXT,
    
    -- Frequency
    frequency INTEGER NOT NULL,
    last_seen INTEGER,
    last_outcome TEXT,
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    rebuilt_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_patterns_domain ON patterns(domain);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);


-- ============================================================================
-- MINISTER_CALIBRATION — Credibility Tracking
-- ============================================================================
-- Per-minister, per-domain accuracy calibration.
-- Starts at 0.50. Moves slowly. Never resets.

CREATE TABLE IF NOT EXISTS minister_calibration (
    minister TEXT NOT NULL,
    domain TEXT NOT NULL,
    confidence REAL NOT NULL,        -- 0.0-1.0
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY(minister, domain)
);

CREATE INDEX IF NOT EXISTS idx_calibration_minister ON minister_calibration(minister);
CREATE INDEX IF NOT EXISTS idx_calibration_domain ON minister_calibration(domain);


-- ============================================================================
-- OVERRIDES — Counsel Ignored Log
-- ============================================================================
-- When sovereign ignores counsel.
-- Feeds into bluntness progression.

CREATE TABLE IF NOT EXISTS overrides (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    
    domain TEXT NOT NULL,
    counsel_posture TEXT NOT NULL,
    actual_action TEXT NOT NULL,
    override_reason TEXT,
    
    -- Outcome (filled later)
    outcome_result TEXT,
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(event_id) REFERENCES events(id)
);

CREATE INDEX IF NOT EXISTS idx_overrides_domain ON overrides(domain);
CREATE INDEX IF NOT EXISTS idx_overrides_outcome ON overrides(outcome_result);


-- ============================================================================
-- METADATA — Schema versioning
-- ============================================================================

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO metadata (key, value) 
VALUES ('schema_version', '1.0');
INSERT OR IGNORE INTO metadata (key, value) 
VALUES ('created_at', datetime('now'));
