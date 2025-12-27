# Technical Specification - Cold Strategist CLI & War Mode Learning

## System Overview

**Cold Strategist** is a Sovereign Counsel Engine that provides:

1. **War Mode**: Safe, abstract adversarial analysis
2. **CLI Interface**: Command-line entry point with argument parsing
3. **Persistent Memory**: SQLite-backed event ledger
4. **Pattern Detection**: Identify recurring behavioral patterns
5. **Adaptive Calibration**: Adjust N's advice based on learned patterns

## Architecture

### Layer Stack

```
┌─────────────────────────────────────────────┐
│           CLI (cli/)                        │
│  args.py | prompts.py | render.py | main.py│
└─────────────────────────────────────────────┘
                    ↑↓
┌─────────────────────────────────────────────┐
│      Orchestrator (core/orchestrator/)       │
│      router.py | engine.py                  │
└─────────────────────────────────────────────┘
                    ↑↓
┌──────────────────────┬──────────────────────┐
│   War Mode           │   Normal Mode        │
│  (core/war/)         │   (darbar/tribunal)  │
│  WarEngine.run()     │   Tribunal.render()  │
└──────────────────────┴──────────────────────┘
                    ↑↓
┌─────────────────────────────────────────────┐
│      Memory Layer (core/memory/)            │
│  memory_store.py | event_log.py |           │
│  pattern_engine.py | override_tracker.py    │
└─────────────────────────────────────────────┘
                    ↑↓
┌─────────────────────────────────────────────┐
│  SQLite Database (data/memory/)             │
│  cold_strategist.db                         │
└─────────────────────────────────────────────┘
```

## CLI Specification

### Entry Points

**Primary**: `python cold.py <mode> [options]`
**Outcome**: `python cold_outcome.py <event-id> --mode <mode>`

### Arguments (cli/args.py)

#### Required
- `mode`: `normal` | `war`
- `--domain`: `career` | `negotiation` | `self` | `fictional` | `other`

#### Optional (with defaults)
- `--stakes`: `low` | `medium` (default) | `high` | `existential`
- `--emotional-load`: 0.0-1.0 (default: 0.3)
- `--urgency`: 0.0-1.0 (default: 0.3)
- `--fatigue`: 0.0-1.0 (default: 0.3)

#### War-Mode Specific
- `--arena` (required for war): `career` | `negotiation` | `self-discipline` | `fictional`
- `--constraints`: space-separated list (e.g., `reversible minimal_collateral legal`)

#### Optional Flags
- `--log-memory`: enable memory logging (default: True)
- `--analyze-patterns`: run pattern detection post-analysis (default: False)

### Argument Validation (cli/args.py::validate_args)

```python
def validate_args(args):
    # War mode requires --arena
    if args.mode == "war" and not args.arena:
        raise ValueError("--arena required for war mode")
    
    # All float args in [0, 1] range
    for param in [emotional_load, urgency, fatigue]:
        if not (0.0 <= param <= 1.0):
            raise ValueError(f"{param} must be 0.0-1.0")
```

### Input Collection (cli/prompts.py)

**collect_context(args)** → (Context, State)

```python
class Context:
    raw_text: str          # User's situation description
    domain: str            # From CLI arg
    stakes: str            # From CLI arg
    emotional_load: float  # From CLI arg
    reversibility: str     # Derived from stakes
    compounding: bool      # True if high/existential stakes
    arena: str             # War mode only
    constraints: List[str] # War mode only

class State:
    emotional_load: float  # From CLI arg
    urgency: float         # From CLI arg
    fatigue: float         # From CLI arg
    stakes: str            # From CLI arg
    time_pressure: float   # Alias for urgency
    resources: float       # 1.0 - fatigue (inverse)
    opponent_hostility: float  # War mode only
```

### Output Rendering (cli/render.py)

Functions format and display results:

- **render_verdict(verdict)**: Display war/normal verdict
- **render_patterns(patterns)**: Display detected patterns
- **render_calibration(posture)**: Display N's adjusted posture
- **render_learning_summary(text)**: Display learning summary
- **render_error(msg)**: Display error message

## Orchestrator Specification

### Router (core/orchestrator/router.py)

**route(mode)** → callable

```python
def route(mode):
    if mode == "war":
        return WarEngine().run  # core/war/war_engine.py
    elif mode == "normal":
        return Tribunal().render  # core/darbar/tribunal.py
    else:
        raise ValueError(f"Unknown mode: {mode}")
```

**route_calibration(mode)** → dict of callables

```python
{
    "calibrate": calibrate_function,
    "posture": posture_function,
    "summary": summary_function
}
```

### Engine (core/orchestrator/engine.py)

**run_analysis(mode, context, state, log_to_memory, analyze_patterns)** → result_dict

```python
result = {
    "mode": str,
    "verdict": dict,           # From engine
    "event_id": str | None,    # From war_memory.log_war_event()
    "patterns": List[Pattern] | None,
    "calibration": dict | None,
    "context": Context,
    "state": State
}
```

## War Mode Specification

### WarEngine (core/war/war_engine.py)

**WarEngine().run(objective, arena, constraints, state, ministers, log_to_memory)** → verdict_dict

```python
verdict = {
    "VERDICT": "PROCEED | CONDITIONAL | ABORT",
    "PRIMARY_MOVE": str,       # Recommended action
    "ALTERNATIVES": List[str], # Other options
    "RISK": float,             # 0-1 scale
    "REVERSIBLE": bool,
    "OPTIONALITY": str,        # "preserved" | "limited"
    "DO_NOT": List[str],       # Constraints
    "NEXT": str,               # First step
    "EVENT_ID": str | None,    # If log_to_memory=True
    ... (other war-specific fields)
}
```

### War Memory (core/war/war_memory.py)

**log_war_event(objective, arena, verdict, state, ministers)** → event_id

```python
# Creates MemoryEvent with:
event = MemoryEvent(
    domain="war",
    stakes=heuristic_from_risk,    # Inferred from verdict risk
    emotional_load=map_from_fatigue(state.fatigue),
    ministers_called=ministers,
    verdict_position=verdict["PRIMARY_MOVE"],
    verdict_posture=verdict["VERDICT"]
)

# Persists to SQLite via MemoryStore.save_event()
# Returns event.event_id (UUID)
```

**resolve_war_outcome(event_id, outcome)** → outcome_record

```python
outcome = {
    "result": "success" | "partial" | "failure",
    "damage": float,           # 0-1 actual damage
    "benefit": float,          # 0-1 value gained
    "lessons": List[str]       # Key learnings
}

# Persists to SQLite via MemoryStore.save_outcome()
```

**log_war_override(event_id, decision_made, override_reason, expected_damage)** → None

```python
# Records that sovereign ignored counsel
# Persists to SQLite via MemoryStore.save_override()
```

### War Calibration (core/war/war_calibration.py)

**calibrate_n_from_war_patterns()** → calibrations_dict

```python
# Loads all events from memory
# Detects war patterns via PatternEngine
# Adjusts calibrations based on patterns:

{
    "war_caution": float,           # Default 1.0
                                    # < 1.0 = more cautious
    "war_urgency_threshold": float, # Default 1.0
                                    # > 1.0 = higher bar
    "war_bluntness": float          # Default 1.0
                                    # > 1.0 = more direct
}

# Heuristics:
# - escalation_bias detected → caution *= 0.7
# - false_urgency_loop detected → urgency_threshold *= 1.5
# - repeated_overrides detected → bluntness *= 1.3

# Persists to SQLite via MemoryStore.save_calibrations()
```

**get_n_war_posture(calibrations)** → posture_dict

```python
{
    "domain": "war",
    "caution": float,
    "urgency_threshold": float,
    "bluntness": float,
    "description": str  # Human-readable posture summary
}
```

**summarize_war_learning()** → str

```python
# Returns human-readable summary of:
# - Number of war events
# - Patterns detected
# - N's adjusted posture
# - Explanation of how N will behave differently
```

## Memory Specification

### Event Storage (core/memory/memory_store.py)

**MemoryStore.save_event(event: MemoryEvent)**

Persists to `events` table in SQLite:
```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    timestamp INTEGER,
    session_index INTEGER,
    domain TEXT,
    stakes TEXT,
    emotional_load REAL,
    urgency REAL,
    ministers_called TEXT (JSON),
    verdict TEXT,
    posture TEXT,
    illusions_detected TEXT (JSON),
    contradictions_found INTEGER,
    sovereign_action TEXT,
    action_followed_counsel BOOLEAN,
    override_reason TEXT
)
```

**MemoryStore.save_outcome(event_id, result, damage, benefit, lessons)**

Persists to `outcomes` table:
```sql
CREATE TABLE outcomes (
    id TEXT PRIMARY KEY,
    event_id TEXT FOREIGN KEY,
    resolved_at INTEGER,
    result TEXT,
    damage REAL,
    benefit REAL,
    lessons TEXT (JSON)
)
```

### Pattern Detection (core/memory/pattern_engine.py)

**PatternEngine.detect_patterns(events)** → List[Pattern]

Detects 7 pattern types:

1. **repetition_loop**: Same domain + same illusion ≥2x
2. **override_loop**: Repeated overrides in same domain ≥2x
3. **emotional_loop**: High-emotion situations in same domain ≥2x
4. **outcome_pattern**: Consistent outcomes in context (≥70% consistency)
5. **war_escalation_bias**: Escalation moves with avg damage >0.3
6. **war_false_urgency_loop**: High urgency decisions with >50% failure
7. **war_repeated_overrides**: Override pattern with tracked success rate

```python
class Pattern:
    pattern_name: str          # e.g., "war_escalation_bias"
    pattern_type: str          # e.g., "war_pattern"
    frequency: int             # How many times detected
    domain: str | None
    illusion_type: str | None
    last_outcome: str | None   # Last known outcome
```

## Data Flow

### Decision Analysis Phase

```
USER SITUATION
    ↓
WarEngine.run()
    ├─ opponent_model() - abstract system
    ├─ generate_moves() - legal only
    ├─ counter_simulator() - simulate counters
    ├─ damage_envelope() - evaluate risk
    └─ build_verdict() - structured output
    ↓
VERDICT with EVENT_ID (if log_to_memory)
    ↓
CLI renders verdict + saves EVENT_ID
```

### Outcome Resolution Phase (days/weeks later)

```
USER OUTCOME
    ↓
resolve_war_outcome(event_id, outcome)
    ├─ MemoryStore.save_outcome()
    │   └─ Insert outcome row in SQLite
    │
    ├─ PatternEngine.detect_patterns()
    │   ├─ Loads all events (including updated outcome)
    │   ├─ Detects all 7 pattern types
    │   └─ Returns updated Pattern list
    │
    └─ calibrate_n_from_war_patterns()
        ├─ For each pattern detected:
        │   ├─ escalation_bias → caution *= 0.7
        │   ├─ false_urgency → urgency *= 1.5
        │   └─ repeated_overrides → bluntness *= 1.3
        │
        └─ MemoryStore.save_calibrations()
            └─ Persist adjusted N calibrations
```

### Next Decision Phase

```
SIMILAR SITUATION ARISES
    ↓
WarEngine.run()
    ├─ Load N's calibrations from memory
    ├─ Apply adjustments (more cautious? more blunt?)
    ├─ Run analysis with adjusted N
    └─ Verdict reflects learned patterns
    ↓
N IS SMARTER (shaped by past outcomes)
```

## Persistence

### SQLite Database

**Location**: `data/memory/cold_strategist.db`

**Tables**:
- `events`: Immutable decision records
- `outcomes`: Delayed outcome resolution
- `patterns`: Detected recurring behaviors
- `overrides`: When counsel was ignored
- `calibrations`: N's confidence adjustments
- `ministers_called`: Participation log

**Guarantees**:
- INSERT-only (no UPDATE/DELETE on events)
- ACID transactions
- Queryable for analysis
- Portable backup

## Testing

### Test Files

**tests/test_cli_integration.py**
- Tests argument parsing
- Tests context/state collection
- Tests end-to-end analysis flow

**tests/test_war_learning_flow.py**
- Tests WarEngine → memory → patterns → calibration
- Tests all 6 stages of war mode learning

### Running Tests

```bash
python tests/test_cli_integration.py
python tests/test_war_learning_flow.py
```

Both should pass with ✓ marks.

## Error Handling

### CLI Argument Errors
- Missing required arg → Show help + exit
- Invalid flag value → Show validation error + exit
- Type error → Convert or show error

### Analysis Errors
- MemoryStore unavailable → Fail silently (event_id still returned)
- Pattern detection fails → Continue (no patterns shown)
- N calibration fails → Use defaults

### User Interruption
- Ctrl+C during input → Graceful exit

## Performance

- **Event logging**: O(1) SQLite insert
- **Pattern detection**: O(n) where n = number of events (typically <1000)
- **Calibration**: O(p) where p = number of patterns (typically <20)
- **Rendering**: O(1) for verdict, O(p) for patterns

No performance issues expected for typical usage.

## Security

- No network calls (purely local)
- No data exfiltration
- SQLite file is plaintext (not encrypted) - users can inspect
- No credentials or secrets

## Constraints & Limitations

- War mode is abstract (no real-world optimization possible)
- Patterns require ≥2 events with outcomes (need history)
- N can't force decisions (only advises)
- All moves must be reversible and legal
- Pattern threshold is fixed at 2 occurrences

---

**Document Version**: 1.0
**Date**: December 27, 2025
**Status**: Complete and Ready for Use
