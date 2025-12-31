from typing import List, Dict, Any
from core.clarification.triggers import needs_clarification
from core.clarification.question_planner import plan_questions
from core.clarification.llm_questioner import ask
from core.clarification.answer_updater import apply_answer
from core.clarification.analytics import ClarificationAnalytics, ClarificationEvent
from core.clarification.impact import compute_impact
import json
import os
from pathlib import Path


TELEMETRY_DIR = Path(__file__).resolve().parents[3] / "data" / "telemetry"
os.makedirs(TELEMETRY_DIR, exist_ok=True)
CLAR_PATH = TELEMETRY_DIR / "clarification_events.jsonl"


def _log_event(event: Dict[str, Any]):
    try:
        with open(CLAR_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


# in-memory analytics collector
analytics = ClarificationAnalytics()


def clarification_loop(context: Dict[str, Any], interventions: List[Dict[str, Any]], resolution: Dict[str, Any], state: Dict[str, Any], decision_id: str = None) -> (Dict[str, Any], Dict[str, Any]):
    reasons = needs_clarification(context, interventions, resolution, state)
    if not reasons:
        return context, state

    plans = plan_questions(reasons, context, [])
    loop_summary = {"decision_id": decision_id, "reasons": reasons, "qa": []}

    for p in plans:
        # snapshot before state for impact computation
        before_state = dict(state) if isinstance(state, dict) else state

        q = ask(p, context)
        # Record question
        qa = {"owner": p.get("owner"), "goal": p.get("goal"), "question": q, "answer": None}
        # Ask interactively (blocking) — caller may replace with non-interactive answers
        try:
            print(f"\n[N asks]: {q}")
            a = input("> ")
        except Exception:
            a = ""

        # Apply answer
        context, state = apply_answer(context, state, a)
        qa["answer"] = a
        loop_summary["qa"].append(qa)

        # compute impact and log to in-memory analytics
        try:
            event = ClarificationEvent(q, a, p.get("owner"), p.get("goal"))
            impact = compute_impact(before_state, state)
            analytics.attach_impact(event, impact)
            analytics.log(event)
        except Exception:
            # keep telemetry best-effort
            pass

        # Log event per Q/A to persistent JSONL
        _log_event({
            "decision_id": decision_id,
            "owner": p.get("owner"),
            "goal": p.get("goal"),
            "question": q,
            "answer": a,
            "state_after": {"clarity": state.get("clarity"), "emotional_load": state.get("emotional_load")},
        })

        if float(state.get("clarity", 0.0)) >= 0.8:
            break

    # final summary log
    _log_event({"decision_id": decision_id, "summary": loop_summary})

    # persist analytics to telemetry directory (best-effort)
    try:
        from pathlib import Path
        analytics_path = TELEMETRY_DIR / "clarification_analytics.jsonl"
        analytics.persist(analytics_path)
    except Exception:
        pass

    return context, state
