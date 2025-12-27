"""
Integration Test: War Mode → Memory → Pattern Detection → N Calibration

Validates the complete flow:
  WarEngine
     ↓
  War Verdict
     ↓
  Event Logged (SQLite)
     ↓
  Decision / Override
     ↓
  Outcome Logged (later)
     ↓
  Pattern Engine
     ↓
  N Bias Adjustment
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.war.war_engine import WarEngine
from core.war.war_memory import log_war_event, resolve_war_outcome, log_war_override
from core.memory.memory_store import MemoryStore
from core.memory.pattern_engine import PatternEngine
from core.war.war_calibration import calibrate_n_from_war_patterns, get_n_war_posture, summarize_war_learning


def test_war_mode_learning_flow():
    """Test complete war mode learning pipeline."""
    
    print("\n" + "="*70)
    print("WAR MODE LEARNING FLOW TEST")
    print("="*70 + "\n")
    
    # Stage 1: Create WarEngine and run analysis
    print("STAGE 1: War Verdict Generation")
    print("-" * 70)
    
    engine = WarEngine()
    
    objective = "Neutralize escalating tension without permanent damage"
    arena = "self-discipline"
    constraints = ["reversible", "minimal_collateral", "exit_route_preserved"]
    state = {
        "fatigue": 0.4,
        "resources": 0.6,
        "time_pressure": 0.5,
        "opponent_hostility": 0.7
    }
    
    verdict = engine.run(
        objective=objective,
        arena=arena,
        constraints=constraints,
        state=state,
        ministers=["Power", "Timing", "Risk", "Truth", "N"],
        log_to_memory=False  # We'll log explicitly
    )
    
    print(f"✓ Verdict generated: {verdict.get('VERDICT')}")
    print(f"  Primary move: {verdict.get('PRIMARY_MOVE')}")
    print(f"  Risk: {verdict.get('RISK'):.2f}")
    print(f"  Reversible: {verdict.get('REVERSIBLE')}")
    
    # Stage 2: Log event to memory
    print("\nSTAGE 2: Event Logging (SQLite)")
    print("-" * 70)
    
    event_id = log_war_event(
        objective=objective,
        arena=arena,
        verdict=verdict,
        state=state,
        ministers=["Power", "Timing", "Risk", "Truth", "N"]
    )
    
    print(f"✓ Event logged to SQLite: {event_id}")
    
    # Stage 3: Sovereign decision and override
    print("\nSTAGE 3: Decision & Override Logging")
    print("-" * 70)
    
    sovereign_decision = "Escalated despite counsel"
    was_override = sovereign_decision != verdict.get("PRIMARY_MOVE")
    
    if was_override:
        log_war_override(
            event_id=event_id,
            decision_made=sovereign_decision,
            override_reason="Felt immediate action necessary",
            expected_damage=0.65
        )
        print(f"✓ Override logged")
        print(f"  Decision: {sovereign_decision}")
        print(f"  Reason: Felt immediate action necessary")
    else:
        print(f"✓ Counsel followed: {sovereign_decision}")
    
    # Stage 4: Outcome resolution (simulated later)
    print("\nSTAGE 4: Outcome Resolution (later)")
    print("-" * 70)
    
    outcome = {
        "result": "failure",
        "damage": 0.72,
        "benefit": 0.1,
        "lessons": ["Escalation created unintended hostility", "Exit route became blocked"]
    }
    
    resolved = resolve_war_outcome(event_id=event_id, outcome=outcome)
    print(f"✓ Outcome resolved: {resolved['outcome']}")
    print(f"  Damage: {resolved['outcome_damage']:.2f}")
    print(f"  Lessons learned: {len(resolved['outcome_lessons'])}")
    
    # Stage 5: Pattern detection
    print("\nSTAGE 5: Pattern Detection")
    print("-" * 70)
    
    store = MemoryStore()
    events = store.load_events()
    
    engine = PatternEngine()
    patterns = engine.detect_patterns(events)
    
    print(f"✓ Pattern scan complete")
    print(f"  Total events in memory: {len(events)}")
    print(f"  Patterns detected: {len(patterns)}")
    
    if patterns:
        for p in patterns:
            if p.domain == "war":
                print(f"  - {p.pattern_name} (frequency: {p.frequency})")
    
    # Stage 6: N Bias Adjustment
    print("\nSTAGE 6: N Bias Adjustment")
    print("-" * 70)
    
    calibrations = calibrate_n_from_war_patterns()
    posture = get_n_war_posture(calibrations)
    
    print(f"✓ N calibrations updated")
    print(f"  Caution factor: {calibrations.get('war_caution', 1.0):.2f}")
    print(f"  Urgency threshold: {calibrations.get('war_urgency_threshold', 1.0):.2f}")
    print(f"  Bluntness factor: {calibrations.get('war_bluntness', 1.0):.2f}")
    print(f"  Posture: {posture['description']}")
    
    # Final summary
    print("\nLEARNING SUMMARY")
    print("-" * 70)
    learning = summarize_war_learning()
    print(learning)
    
    print("\n" + "="*70)
    print("✓ WAR MODE LEARNING FLOW COMPLETE")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test_war_mode_learning_flow()
        print("TEST PASSED\n")
    except Exception as e:
        print(f"\nTEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
