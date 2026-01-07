# Flow Diagram: War Mode → Memory → Pattern Detection → N Calibration

## Visual Flow

```
USER
  │
  ├─ cold.py normal --domain career --stakes high
  │
  └─ cold.py war --domain negotiation --arena career --stakes high
           │
           ↓
    ┌─────────────────────┐
    │  CLI/Args Parser    │ ← cli/args.py
    │  (validate flags)   │
    └──────────┬──────────┘
               ↓
    ┌─────────────────────┐
    │  CLI/Prompts        │ ← cli/prompts.py
    │  (user inputs       │
    │   situation)        │
    └──────────┬──────────┘
               ↓
    ┌─────────────────────────────┐
    │  Orchestrator/Router        │ ← core/orchestrator/router.py
    │  (select war vs normal)     │
    └──────────┬──────────────────┘
               │
        ┌──────┴──────┐
        ↓             ↓
    ┌─────────┐  ┌──────────┐
    │ War Mode │  │Normal    │
    │         │  │Mode      │
    └────┬────┘  └──────────┘
         │
         ↓
    ┌────────────────────────────────────┐
    │  WarEngine.run()                   │ ← core/war/war_engine.py
    │                                    │
    │  Coordinates:                      │
    │  • opponent_model()               │ ← core/war/opponent_model.py
    │  • generate_moves()               │ ← core/war/move_generator.py
    │  • simulate_counters()            │ ← core/war/counter_simulator.py
    │  • evaluate_damage()              │ ← core/war/damage_envelope.py
    │  • build_verdict()                │ ← core/war/war_verdict.py
    └────┬────────────────────────────────┘
         ↓
    ┌──────────────────┐
    │ War Verdict      │
    │ {               │
    │  VERDICT: ...,  │
    │  PRIMARY_MOVE   │
    │  RISK: 0.45,    │
    │  REVERSIBLE,    │
    │  OPTIONALITY,   │
    │  DO_NOT: [...]  │
    │ }               │
    └────┬────────────┘
         │
         ├─ log_to_memory = True?
         │
         ├→ YES
         │   ↓
         │   ┌──────────────────────┐
         │   │ log_war_event()      │ ← core/war/war_memory.py
         │   │ (create MemoryEvent) │
         │   └────────┬─────────────┘
         │            ↓
         │   ┌──────────────────────────────┐
         │   │ MemoryStore.save_event()     │ ← core/memory/memory_store.py
         │   │ (SQLite INSERT)              │
         │   └────────┬─────────────────────┘
         │            ↓
         │   ┌──────────────────────────────┐
         │   │ SQLite event_log table       │ ← data/memory/cold_strategist.db
         │   │ (immutable ledger)           │
         │   └────────┬─────────────────────┘
         │            ↓
         │   EVENT_ID = uuid()
         │   (saved for later outcome resolution)
         │
         └→ NO: EVENT_ID = None
         │
         ↓
    ┌──────────────────────┐
    │ Orchestrator/Engine  │ ← core/orchestrator/engine.py
    │ (handle post-verdict)│
    └────┬─────────────────┘
         │
         ├─ analyze_patterns = True?
         │
         ├→ YES
         │   ↓
         │   ┌──────────────────────────┐
         │   │ MemoryStore.load_events()│
         │   │ (read all SQLite events) │
         │   └────────┬─────────────────┘
         │            ↓
         │   ┌──────────────────────────┐
         │   │ PatternEngine            │ ← core/memory/pattern_engine.py
         │   │ .detect_patterns()       │
         │   │                          │
         │   │ Detects:                 │
         │   │ • repetition_loop        │
         │   │ • override_loop          │
         │   │ • emotional_loop         │
         │   │ • outcome_pattern        │
         │   │ • war_escalation_bias    │
         │   │ • war_false_urgency_loop │
         │   │ • war_repeated_overrides │
         │   └────────┬─────────────────┘
         │            ↓
         │   ┌──────────────────────────┐
         │   │ Patterns List            │
         │   │ (with frequency, domain) │
         │   └────────┬─────────────────┘
         │            ↓
         │   ┌──────────────────────────┐
         │   │ calibrate_n_from_war_    │ ← core/war/war_calibration.py
         │   │ patterns()               │
         │   │                          │
         │   │ For each pattern:        │
         │   │ • escalation_bias →      │
         │   │   caution *= 0.7         │
         │   │ • false_urgency_loop →   │
         │   │   urgency_threshold*=1.5 │
         │   │ • repeated_overrides →   │
         │   │   bluntness *= 1.3       │
         │   └────────┬─────────────────┘
         │            ↓
         │   ┌──────────────────────────┐
         │   │ N's Adjusted Posture     │
         │   │ {                        │
         │   │  caution: 0.70,          │
         │   │  urgency_threshold: 1.5, │
         │   │  bluntness: 1.0          │
         │   │ }                        │
         │   └────────┬─────────────────┘
         │            ↓
         │   ┌──────────────────────────┐
         │   │ MemoryStore.             │
         │   │ save_calibrations()      │
         │   │ (persist N's adjustments)│
         │   └──────────────────────────┘
         │
         └→ NO: No pattern analysis
         │
         ↓
    ┌──────────────────────┐
    │ CLI/Render           │ ← cli/render.py
    │ • render_verdict()   │
    │ • render_patterns()  │
    │ • render_calibration │
    │ • render_learning()  │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────┐
    │ User sees verdict    │
    │ and event_id         │
    │ (if logged)          │
    └──────────┬───────────┘
               │
               │ (days/weeks later)
               │
               ↓
    ┌──────────────────────┐
    │ python cold_outcome  │
    │ <event_id>           │
    │ --mode war           │
    └────┬─────────────────┘
         ↓
    ┌──────────────────────┐
    │ CLI/Prompts          │
    │ collect_outcome()    │
    │ • result             │
    │ • damage             │
    │ • benefit            │
    │ • lessons            │
    └────┬─────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ resolve_war_outcome()            │ ← core/war/war_memory.py
    │ (map to SQLite)                  │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ MemoryStore.save_outcome()       │ ← core/memory/memory_store.py
    │ (SQLite INSERT outcome row)      │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ SQLite outcome table             │ ← data/memory/cold_strategist.db
    │ (outcome now linked to event)    │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ PatternEngine.detect_patterns()  │
    │ (RE-RUN with updated outcome)    │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ Updated Patterns                 │
    │ (escalation_bias now freq 4)     │
    │ (false_urgency_loop now freq 3)  │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ calibrate_n_from_war_patterns()  │
    │ (RE-CALCULATE N's calibration)   │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ N's Re-Adjusted Posture          │
    │ {                                │
    │  caution: 0.50 (more cautious)   │
    │  urgency_threshold: 1.80 (higher)│
    │  bluntness: 1.0 (unchanged)      │
    │ }                                │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ MemoryStore.save_calibrations()  │
    │ (persist updated N calibrations) │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ CLI/Render                       │
    │ • render outcome                 │
    │ • render patterns                │
    │ • render learning summary        │
    └────┬─────────────────────────────┘
         ↓
    ┌──────────────────────────────────┐
    │ User sees how N learned          │
    │ and will behave differently      │
    │ next similar decision            │
    └──────────────────────────────────┘
         │
         │ (next similar decision)
         │
         ↓
    ┌──────────────────────────────────┐
    │ WarEngine uses N's               │
    │ UPDATED calibrations             │
    │ (more cautious, skeptical,       │
    │  or blunt based on patterns)     │
    │                                  │
    │ N's advice is shaped by          │
    │ LEARNING from past decisions     │
    └──────────────────────────────────┘
```

## Summary

1. **Decision Cycle**: WarEngine → Verdict → Event Logged
2. **Memory**: Event persists to SQLite (immutable ledger)
3. **Later**: Outcome resolution → Outcome logged to SQLite
4. **Pattern Detection**: PatternEngine scans all events (including new outcome)
5. **Learning**: Patterns inform calibration adjustments to N
6. **Adaptation**: N's posture changes based on what was learned
7. **Next Decision**: N uses updated calibrations → more cautious, direct, or skeptical

## Key Guarantees

- ✅ All events immutable (INSERT-only ledger)
- ✅ Outcomes logged separately (delayed resolution)
- ✅ Patterns re-calculated on each outcome
- ✅ N's calibrations persist (not forgotten between sessions)
- ✅ Learning is accumulating (patterns grow stronger with repetition)
- ✅ Transparent reasoning (full audit trail in SQLite)
