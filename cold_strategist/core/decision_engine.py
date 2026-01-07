from dataclasses import dataclass
from typing import Dict, Any, List

from cold_strategist.core.query_mode import run_query_mode
from cold_strategist.core.prompt_builder import build_minister_prompt
from cold_strategist.core.tribunal_rules import should_trigger_tribunal
from cold_strategist.core.tribunal_engine import tribunal_decision
from cold_strategist.context.context_builder import ContextBuilder


@dataclass
class MinisterOutput:
    minister_id: str
    content: Dict[str, Any]
    confidence: float


def retrieve_relevant_doctrine(question: str, book_context: Any) -> List[str]:
    # Minimal retrieval: return book_context chunks if provided, or empty list
    if not book_context:
        return []
    if isinstance(book_context, list):
        return book_context
    return [str(book_context)]


def post_process(ministers: Dict[str, Any], raw_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simple deterministic post-processing:
      - compute disagreement as fraction of ministers not matching majority proceed flag
      - if no outputs or low confidence majority -> SILENCE
    """
    if not raw_outputs:
        return {"decision": "SILENCE", "disagreement": 1.0}

    # Map minister -> proceed bool
    proceed_map = {}
    confidences = []
    for mid, o in raw_outputs.items():
        content = o.get("content", {}) or {}
        proceed = bool(content.get("proceed") is True)
        proceed_map[mid] = proceed
        confidences.append(float(o.get("confidence", 0.0) or 0.0))

    # Majority proceed?
    proceeds = sum(1 for v in proceed_map.values() if v)
    total = max(1, len(proceed_map))
    majority_fraction = proceeds / total

    # disagreement heuristic: fraction opposing majority
    disagreement = 1.0 - max(majority_fraction, 1 - majority_fraction)

    # Silence if average confidence low
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    if avg_conf < 0.5:
        return {"decision": "SILENCE", "disagreement": disagreement}

    # Otherwise produce post object
    return {"decision": "ADVICE", "disagreement": disagreement, "outputs": raw_outputs}


def decide(
    question: str,
    book_context,
    ministers: Dict[str, Any],
    llm,
    mode: str = "FAST_READ_ONLY",
) -> Dict[str, Any]:
    # Step 0: Read-only enforcement
    context = run_query_mode(mode)
    if context is not None:
        context.enforce("query")

    # Context building / Gatekeeper: ensure structured context before proceeding
    cb = ContextBuilder()
    ctx = cb.create_context(question)
    # If more input required, return the next clarifying question
    if cb.needs_more_input(ctx):
        # Build active_required_fields mapping from ministers' output_shape
        active_required_fields = {}
        active_ministers = list(ministers.keys()) if ministers else []
        for mid, m in (ministers or {}).items():
            try:
                reqs = m.output_shape.get("required_fields", [])
            except Exception:
                reqs = []
            active_required_fields[mid] = reqs

        # decision id
        import uuid
        decision_id = f"DEC-{uuid.uuid4()}"

        next_q = cb.propose_question(ctx, decision_id=decision_id, active_required_fields=active_required_fields, active_ministers=active_ministers)
        return {"decision": "NEED_CONTEXT", "question": next_q}

    # Step 1: Retrieve doctrine (no embedding in read-only mode)
    doctrine_chunks = retrieve_relevant_doctrine(question, book_context)

    # Step 2: Minister analysis
    raw_outputs: Dict[str, Dict[str, Any]] = {}
    for minister_id, minister in ministers.items():
        prompt = build_minister_prompt(minister, "\n\n".join(doctrine_chunks))

        # call LLM (support .generate or callable)
        try:
            if hasattr(llm, "generate"):
                res = llm.generate(prompt=prompt)
            else:
                # support simple callable llm(prompt)
                res = llm(prompt)
        except Exception:
            continue

        parsed = None
        if isinstance(res, dict) and "parsed" in res:
            parsed = res.get("parsed")
        elif isinstance(res, dict) and "content" in res:
            parsed = res.get("content")
        else:
            parsed = res

        # Normalize parsed to dict
        content = parsed if isinstance(parsed, dict) else {}
        confidence = float(content.get("confidence", 0.5) if isinstance(content, dict) else 0.5)

        raw_outputs[minister_id] = {"content": content, "confidence": confidence, "minister_id": minister_id}

    # Step 3: Post-processing
    post = post_process(ministers, raw_outputs)
    if post.get("decision") == "SILENCE":
        return post

    # Step 4: Tribunal check
    disagreement = post.get("disagreement", 0.0)

    # Prepare outputs for tribunal (as expected by tribunal rules)
    outputs_for_tribunal = raw_outputs

    if should_trigger_tribunal(disagreement, outputs_for_tribunal):
        return tribunal_decision(outputs_for_tribunal, disagreement)

    # Step 5: Final sovereign-safe output (return post)
    return post
