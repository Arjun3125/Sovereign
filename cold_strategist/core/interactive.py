"""
Interactive decision runner for Darbar ContextBuilder.

Provides `run_interactive_decision` which loops asking questions via a
user-provided `ask_fn` until context is ready or termination.
"""
from typing import Callable, Dict, Any, Optional
from cold_strategist.context.context_builder import ContextBuilder
import uuid

TERMINATION_STRING = "INSUFFICIENT CONTEXT — NO FURTHER PROGRESS POSSIBLE"


def decision_context_to_state(ctx) -> Dict[str, Any]:
    """Serialize DecisionContext into the canonical context state schema."""
    return {
        "identity": {"domain": ctx.domain},
        "objectives": {},
        "constraints": {},
        "risk_profile": {},
        "time_horizon": {},
        "resources": {},
        "environment": {},
        "forbidden_moves": {},
        "confidence_map": {"overall_context_confidence": ctx.confidence, "unstable_fields": []},
        "meta": {
            "prior_patterns": ctx.prior_patterns,
            "emotional_load": getattr(ctx.emotional_load, 'value', None)
        }
    }


def run_interactive_decision(
    raw_input: str,
    ministers: Dict[str, Any],
    ask_fn: Callable[[str], str],
    max_rounds: int = 10,
    gatekeeper: Optional[Any] = None,
    use_ollama: bool = False,
    ollama_model: Optional[str] = None,
    ollama_timeout: int = 8,
    prime_confidant: Optional[object] = None,
) -> Dict[str, Any]:
    """
    Run the interactive ContextBuilder loop.

    Args:
        raw_input: Sovereign declaration string
        ministers: mapping of minister_id -> minister object (must expose output_shape.required_fields)
        ask_fn: callable(question: str) -> answer: str

    Returns:
        {"status": "CONTEXT_READY", "context_json": {...}} or
        {"status": "TERMINATED", "payload": TERMINATION_STRING}
    """
    cb = ContextBuilder()
    ctx = cb.create_context(raw_input)

    # Compute active ministers via Gatekeeper classifier if provided
    provided_ministers = ministers or {}
    if gatekeeper is not None:
        try:
            active_minister_keys = gatekeeper.ministers_from_text(raw_input, use_ollama=use_ollama, ollama_model=ollama_model, timeout=ollama_timeout, prime_confidant=prime_confidant)
        except Exception:
            active_minister_keys = list(provided_ministers.keys())
    else:
        active_minister_keys = list(provided_ministers.keys())

    # Filter ministers to the active quorum
    active_ministers_map = {k: v for k, v in provided_ministers.items() if k in set(active_minister_keys)}

    # Build active_required_fields map for the filtered ministers
    active_required_fields = {}
    for mid, m in active_ministers_map.items():
        try:
            reqs = m.output_shape.get("required_fields", [])
        except Exception:
            reqs = []
        active_required_fields[mid] = reqs
    active_ministers = list(active_ministers_map.keys())

    decision_id = f"DEC-{uuid.uuid4()}"

    rounds = 0
    while True:
        rounds += 1
        if rounds > max_rounds:
            return {"status": "TERMINATED", "payload": TERMINATION_STRING}

        if not cb.needs_more_input(ctx):
            # Build final structured JSON and return
            final_state = decision_context_to_state(ctx)
            return {"status": "CONTEXT_READY", "context_json": final_state}

        question = cb.propose_question(
            ctx,
            decision_id=decision_id,
            active_required_fields=active_required_fields,
            active_ministers=active_ministers,
            context_state=decision_context_to_state(ctx),
        )

        if question is None or question == TERMINATION_STRING:
            return {"status": "TERMINATED", "payload": TERMINATION_STRING}

        # Ask user (via provided callback)
        answer = ask_fn(question)

        # Update context
        ctx = cb.update_context(ctx, question, answer)
