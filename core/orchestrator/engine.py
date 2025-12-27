"""
Engine - Unified Entry Point for Analysis and Logging

Wraps the routed engine and handles memory logging, pattern analysis, and output.

Includes mode resolution (quick/normal/war) with policy-based escalation.
"""

from typing import Dict, Any, Optional
from cli.prompts import Context, State


def run_analysis(
    mode: str,
    context: Context,
    state: State,
    log_to_memory: bool = True,
    analyze_patterns: bool = False,
    memory_flags: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run analysis with selected engine and optionally log to memory.
    
    Performs mode resolution first (may escalate quick → normal).
    
    Args:
        mode: "quick", "normal", or "war"
        context: Context object
        state: State object
        log_to_memory: Whether to log event to memory
        analyze_patterns: Whether to analyze patterns after analysis
        memory_flags: Memory-derived signals for mode policy
        
    Returns:
        Result dict with verdict, event_id, patterns, calibration
    """
    from core.orchestrator.router import route, route_calibration, resolve_mode_with_policy
    
    # Step 1: Resolve actual mode (may escalate quick → normal)
    actual_mode = resolve_mode_with_policy(
        requested_mode=mode,
        state=state,
        memory_flags=memory_flags or {},
        domain=getattr(context, 'domain', 'unknown')
    )
    
    # Step 2: Get the appropriate engine
    engine = route(actual_mode)
    
    # Step 3: Prepare arguments and execute based on actual mode
    if actual_mode == "quick":
        # Quick Mode: pass context and state directly
        result = engine(
            context=context,
            state=state
        )
    
    elif actual_mode == "war":
        # War mode expects specific parameters
        result = engine(
            objective=context.raw_text,
            arena=getattr(context, 'arena', 'default'),
            constraints=getattr(context, 'constraints', []),
            state={
                "fatigue": getattr(state, 'fatigue', 0.0),
                "resources": getattr(state, 'resources', 'medium'),
                "time_pressure": getattr(state, 'time_pressure', 'low'),
                "emotional_load": getattr(state, 'emotional_load', 0.0)
            },
            log_to_memory=log_to_memory
        )
    
    else:
        # Normal mode (generic call)
        result = engine(context=context, state=state)
    
    # Step 4: Log to memory if enabled
    if log_to_memory and actual_mode == "war" and isinstance(result, dict) and "EVENT_ID" in result:
        event_id = result["EVENT_ID"]
    elif log_to_memory and actual_mode == "quick" and hasattr(result, 'event_id'):
        event_id = result.event_id
    else:
        event_id = None
    
    # Step 5: Analyze patterns if requested
    patterns = None
    calibration = None
    
    if analyze_patterns:
        calibrators = route_calibration(actual_mode)
        patterns = calibrators.get("calibrate", lambda: [])()
        calibration = calibrators.get("posture", lambda: {})()
    
    return {
        "mode": actual_mode,
        "requested_mode": mode,
        "escalated": actual_mode != mode,
        "verdict": result,
        "event_id": event_id,
        "patterns": patterns,
        "calibration": calibration,
        "context": context,
        "state": state
    }


def resolve_outcome(
    event_id: str,
    outcome: Dict[str, Any],
    mode: str = "war"
) -> Dict[str, Any]:
    """
    Resolve the outcome for a previously logged event.
    
    Args:
        event_id: Event ID to resolve
        outcome: Outcome dict (result, damage, benefit, lessons)
        mode: "war" or "normal"
        
    Returns:
        Updated event record
    """
    if mode == "war":
        from core.war.war_memory import resolve_war_outcome
        return resolve_war_outcome(event_id=event_id, outcome=outcome)
    else:
        # Normal mode outcome resolution (not yet implemented)
        return {
            "event_id": event_id,
            "outcome": "not_implemented_for_normal_mode"
        }


def get_learning_summary(mode: str) -> str:
    """
    Get learning summary for mode.
    
    Args:
        mode: "war" or "normal"
        
    Returns:
        Human-readable summary
    """
    from core.orchestrator.router import route_calibration
    
    calibrators = route_calibration(mode)
    summary_fn = calibrators.get("summary", lambda: "No learning summary available.")
    
    return summary_fn()


def run_and_log(engine, context, state):
    """Compatibility wrapper: run engine (callable or object with .run)
    then attempt to persist a memory event via MemoryStore.save_event.

    This is a best-effort helper for simpler CLI integrations that expect
    a single call which both runs analysis and logs the resulting event.
    """
    # Execute engine
    if hasattr(engine, "run") and callable(getattr(engine, "run")):
        result = engine.run(context, state)
    else:
        # Try calling as a plain function
        try:
            result = engine(context=context, state=state)
        except TypeError:
            # Fallback positional
            result = engine(context, state)

    # Try to persist event (best-effort)
    try:
        from core.memory.memory_store import MemoryStore
        from core.memory.event_log import MemoryEvent

        store = MemoryStore()

        # If a MemoryEvent instance is embedded in the result
        if isinstance(result, dict) and isinstance(result.get("memory_event"), MemoryEvent):
            store.save_event(result["memory_event"])

        # If engine returned an event-like dict with EVENT_ID or event_id, construct a minimal MemoryEvent
        elif isinstance(result, dict) and ("EVENT_ID" in result or "event_id" in result):
            eid = result.get("EVENT_ID") or result.get("event_id")

            me = MemoryEvent(
                event_id=eid,
                domain=getattr(context, "domain", "unknown"),
                stakes=getattr(state, "stakes", "medium"),
                emotional_load=str(getattr(state, "emotional_load", "medium")),
                ministers_called=result.get("ministers_called", []),
                verdict_position=(result.get("verdict") if isinstance(result.get("verdict"), str)
                                  else (result.get("verdict", {}).get("position") if isinstance(result.get("verdict"), dict) else "")),
                verdict_posture=result.get("posture") or (result.get("verdict", {}).get("posture") if isinstance(result.get("verdict"), dict) else "")
            )

            store.save_event(me)
    except Exception:
        # Swallow persistence errors to avoid breaking CLI flow
        pass

    return result
