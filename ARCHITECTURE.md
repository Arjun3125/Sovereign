# Cold Strategist - Complete Architecture

## Overview

Cold Strategist is a Sovereign Counsel Engine combining **normal mode** (standard advice) and **war mode** (adversarial analysis) with **persistent memory**, **pattern detection**, and **adaptive calibration**.

The system learns from decisions and their outcomes, adjusting N's (the counsel) posture and bias over time.

## Full Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Entry Point                         │
│                      (cli/main.py)                              │
├─────────────────────────────────────────────────────────────────┤
│ 1. Parse Arguments (cli/args.py)                                │
│    - mode: normal | war                                         │
│    - domain: career, negotiation, self, fictional, other        │
│    - stakes, emotional_load, urgency, fatigue                   │
│    - (war) arena, constraints                                   │
├─────────────────────────────────────────────────────────────────┤
│ 2. Collect Context & State (cli/prompts.py)                     │
│    - User inputs situation description                          │
│    - Builds Context and State objects                           │
├─────────────────────────────────────────────────────────────────┤
│ 3. Route to Engine (core/orchestrator/router.py)                │
│    → War Mode: WarEngine.run(objective, arena, constraints)     │
│    → Normal Mode: Tribunal.render(context, state)               │
├─────────────────────────────────────────────────────────────────┤
│ 4. Generate Verdict                                             │
│    - WarEngine coordinates:                                      │
│      • opponent_model.build_opponent()                          │
│      • move_generator.generate_moves()                          │
│      • counter_simulator.simulate_counters()                    │
│      • damage_envelope.evaluate_damage()                        │
│      • war_verdict.build_war_verdict()                          │
├─────────────────────────────────────────────────────────────────┤
│ 5. Log Event (core/war/war_memory.py)                           │
│    - if log_to_memory == True                                   │
│    - log_war_event() creates MemoryEvent                        │
│    - Event persisted to SQLite (core/memory/memory_store.py)    │
│    - Returns EVENT_ID for outcome resolution                    │
├─────────────────────────────────────────────────────────────────┤
│ 6. Render Verdict (cli/render.py)                               │
│    - Formatted output: verdict, risk, reversibility, options    │
│    - Display EVENT_ID for later outcome logging                 │
├─────────────────────────────────────────────────────────────────┤
│ 7. (Optional) Analyze Patterns (if --analyze-patterns)          │
│    - Load all events from memory                                │
│    - PatternEngine.detect_patterns()                            │
│    - Detect war-specific: escalation_bias, false_urgency_loop   │
│    - Render patterns to terminal                                │
├─────────────────────────────────────────────────────────────────┤
│ 8. (Optional) Calibrate N (core/war/war_calibration.py)         │
│    - calibrate_n_from_war_patterns()                            │
│    - Adjust caution, urgency_threshold, bluntness               │
│    - Get N's updated war posture                                │
│    - Render calibration to terminal                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (days/weeks later)
┌─────────────────────────────────────────────────────────────────┐
│                   Outcome Resolution (CLI)                      │
│                  (cli/main.py::outcome_main)                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Collect Outcome (cli/prompts.py::collect_outcome)            │
│    - User inputs: result, damage, benefit, lessons learned      │
├─────────────────────────────────────────────────────────────────┤
│ 2. Resolve Event (core/orchestrator/engine.py)                  │
│    - resolve_outcome(event_id, outcome)                         │
│    - Calls war_memory.resolve_war_outcome()                     │
│    - Persists outcome to SQLite                                 │
├─────────────────────────────────────────────────────────────────┤
│ 3. Update Memory (core/memory/memory_store.py)                  │
│    - save_outcome(event_id, result, damage, benefit, lessons)   │
│    - Event now marked resolved in event_log.MemoryEvent         │
├─────────────────────────────────────────────────────────────────┤
│ 4. Re-detect Patterns (core/memory/pattern_engine.py)           │
│    - PatternEngine.detect_patterns() on all events              │
│    - Includes new outcome in pattern analysis                   │
│    - _detect_war_patterns() identifies war-specific loops       │
├─────────────────────────────────────────────────────────────────┤
│ 5. Recalibrate N (core/war/war_calibration.py)                  │
│    - calibrate_n_from_war_patterns() with updated patterns      │
│    - Adjusts N's confidence/bluntness for next decision         │
│    - Save updated calibrations to memory                        │
├─────────────────────────────────────────────────────────────────┤
│ 6. Render Learning Summary                                      │
│    - Show patterns detected, frequency, outcomes                │
│    - Display N's adjusted posture                               │
│    - Explain how N will behave differently next time            │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
cold_strategist/
├── cli/                              # Command-line interface
│   ├── __init__.py
│   ├── args.py                       # Argument parsing
│   ├── prompts.py                    # Input collection
│   ├── render.py                     # Output formatting
│   ├── main.py                       # Entry point
│   └── README.md                     # CLI documentation
│
├── core/                             # Core logic
│   ├── war/                          # War mode (safe, abstract)
│   │   ├── war_engine.py             # Orchestrator
│   │   ├── opponent_model.py         # System modeling
│   │   ├── move_generator.py         # Legal move generation
│   │   ├── counter_simulator.py      # Simulate counters
│   │   ├── damage_envelope.py        # Risk evaluation
│   │   ├── war_verdict.py            # Verdict building
│   │   ├── war_memory.py             # Event logging
│   │   ├── war_calibration.py        # N bias adjustment
│   │   └── __init__.py
│   │
│   ├── memory/                       # Persistent memory layer
│   │   ├── memory_store.py           # SQLite persistence
│   │   ├── event_log.py              # MemoryEvent dataclass
│   │   ├── pattern_engine.py         # Pattern detection
│   │   ├── override_tracker.py       # Override logging
│   │   ├── confidence_adjuster.py    # Minister calibration
│   │   ├── database.py               # SQLite interface
│   │   └── __init__.py
│   │
│   ├── orchestrator/                 # CLI orchestration
│   │   ├── router.py                 # Route to war/normal
│   │   ├── engine.py                 # Unified analysis entry
│   │   └── __init__.py
│   │
│   ├── ... (other domains: darbar, ministers, n, etc.)
│   └── orchestrator.py               # Legacy (for compatibility)
│
├── tests/
│   ├── test_cli_integration.py       # CLI integration tests
│   ├── test_war_learning_flow.py     # War mode + memory flow
│   ├── test_war_mode.py              # War engine tests
│   ├── test_ministers.py             # Minister tests
│   └── ...
│
├── cold.py                           # Main entry point (python cold.py)
├── cold_outcome.py                   # Outcome entry point
├── README.md                         # Project README
└── ...
```

## Key Components

### 1. CLI Layer (cli/)
- **Responsibility**: Parse args, collect input, render output
- **Key Files**:
  - `args.py`: Validates command-line flags
  - `prompts.py`: Collects situation and outcome info
  - `render.py`: Formats verdicts, patterns, calibrations
  - `main.py`: Orchestrates entire user interaction
- **Entry Points**:
  - `cold.py`: Normal/war analysis
  - `cold_outcome.py`: Outcome resolution

### 2. Orchestrator (core/orchestrator/)
- **Responsibility**: Route to appropriate engine, handle memory logging
- **Key Files**:
  - `router.py`: Selects war or normal mode engine
  - `engine.py`: Unified interface; calls router, logging, pattern analysis
- **Interface**: Called by CLI main.py

### 3. War Mode (core/war/)
- **Responsibility**: Safe, abstract adversarial analysis
- **Key Files**:
  - `war_engine.py`: Orchestrator; coordinates all components
  - `opponent_model.py`: Model the system/opponent abstractly
  - `move_generator.py`: Generate legal, reversible moves only
  - `counter_simulator.py`: Simulate potential counters
  - `damage_envelope.py`: Evaluate risk/damage
  - `war_verdict.py`: Build structured verdict
  - `war_memory.py`: Log events to SQLite
  - `war_calibration.py`: Adjust N's posture based on patterns
- **Safety Guarantees**:
  - All moves are legal and reversible
  - No real-world harm (fictional/game/negotiation context)
  - Transparent reasoning (full trace of analysis)

### 4. Memory Layer (core/memory/)
- **Responsibility**: Persistent event storage, pattern detection, calibration
- **Key Files**:
  - `memory_store.py`: SQLite API (INSERT-only ledger)
  - `event_log.py`: MemoryEvent dataclass; immutable event record
  - `pattern_engine.py`: Detect repetition, override, emotional loops + war patterns
  - `override_tracker.py`: Log when sovereign ignores counsel
  - `confidence_adjuster.py`: Store minister/N calibrations
  - `database.py`: Low-level SQLite interface
- **Guarantees**:
  - Events are immutable (INSERT-only)
  - Outcomes logged separately, delayed
  - Patterns re-calculated on each outcome resolution
  - N's calibrations persist across sessions

## Examples

### War Mode Example

```bash
python cold.py war \
  --domain negotiation \
  --arena career \
  --stakes high \
  --constraints reversible minimal_collateral \
  --analyze-patterns
```

**User Input:**
```
Describe the situation:
> Counterparty demands unfavorable terms with 48-hour deadline
```

**Output:**
1. War Verdict (risk 45%, reversible, options preserved)
2. Event logged: `a3f7c2e1-9b4d-4a2c-8f1d-2b5e...`
3. Patterns detected (if history exists):
   - `war_escalation_bias` (frequency 3)
   - `war_false_urgency_loop` (frequency 2)
4. N's Adjusted Posture:
   - Caution: 0.70x (more cautious on escalation)
   - Urgency threshold: 1.50x (higher bar for urgency claims)

### Outcome Resolution Example (days later)

```bash
python cold_outcome.py a3f7c2e1-9b4d-4a2c-8f1d-2b5e... --mode war
```

**User Input:**
```
Outcome result:
> failure

Actual damage:
> 0.72

Benefit:
> 0.1

Lessons:
> Escalation created unintended hostility, Exit route became blocked
```

**Output:**
- Outcome persisted
- Patterns re-detected (escalation bias now frequency 4)
- N's posture further adjusted (caution 0.50x, urgency 1.80x)
- Learning summary shows N will be even more cautious next time

## Data Flow: Decision → Memory → Learning

```
┌─────────────┐
│   Decision  │
│  Situation  │
│  Context    │
└──────┬──────┘
       ↓
┌─────────────────────────────────┐
│   War Mode Analysis             │
│  - Opponent model               │
│  - Move generation              │
│  - Counter simulation           │
│  - Damage evaluation            │
│  - Verdict building             │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│   Event Logged to SQLite        │
│  - Objective, arena, moves      │
│  - Verdict, risk, reversibility │
│  - STATE at time of decision    │
│  - EVENT_ID for later reference │
└──────┬──────────────────────────┘
       ↓
┌─────────────┐
│   Sovereign │
│   Decides   │  (days/weeks later)
│   & Acts    │
└──────┬──────┘
       ↓
┌─────────────────────────────────┐
│   Outcome Logged to SQLite      │
│  - Result (success/partial/fail)│
│  - Damage/benefit incurred      │
│  - Lessons learned              │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│   Pattern Detection             │
│  - Escalation bias?             │
│  - False urgency?               │
│  - Repeated overrides?          │
│  - What patterns emerged?       │
└──────┬──────────────────────────┘
       ↓
┌─────────────────────────────────┐
│   N Calibration Update          │
│  - Adjust caution/bluntness     │
│  - Raise urgency threshold      │
│  - Increase directness          │
│  - Save to persistent memory    │
└──────┬──────────────────────────┘
       ↓
┌──────────────────────────────────┐
│   Next Similar Decision           │
│  - N uses updated calibration    │
│  - More cautious (or blunt)      │
│  - Patterns inform N's posture   │
│  - Counsel is shaped by learning │
└──────────────────────────────────┘
```

## Persistence

All memories are stored in SQLite (`data/memory/cold_strategist.db`):

- **events**: Core decision analysis (immutable)
- **outcomes**: Decision results (logged later)
- **patterns**: Detected recurring behaviors
- **overrides**: When sovereign ignored counsel
- **calibrations**: Minister/N confidence adjustments
- **ministers_called**: Which ministers participated in each event

## Next Steps

1. **Test the CLI**: Run `python tests/test_cli_integration.py`
2. **Run war mode**: `python cold.py war --domain negotiation --arena career --stakes high`
3. **Test integration**: Run `python tests/test_war_learning_flow.py`
4. **Resolve outcome**: After days, run `python cold_outcome.py <event-id> --mode war`
5. **Monitor learning**: Check patterns and N's adjusted posture

## Safety & Constraints

- ✅ All moves are legal and reversible
- ✅ No direct harm to real entities (abstract analysis)
- ✅ Transparent reasoning (full trace of analysis)
- ✅ Events logged immutably (audit trail)
- ✅ Memory isolated (SQLite, not connected to external systems)
- ✅ User controls all decisions (N only advises)

---

**Last Updated**: December 27, 2025
**Status**: War Mode + Memory + Calibration Complete; CLI Integration Ready
