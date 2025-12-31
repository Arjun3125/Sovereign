"""
Quick Engine - Quick Mode
Fast, streamlined decision making for urgent situations.
"""


class QuickEngine:
    """Provides fast decision-making for urgent situations."""

    def __init__(self):
        """Initialize the quick engine."""
        pass

    def quick_decide(self, situation: dict) -> dict:
        """Make a quick decision on an urgent situation.

        Performs a single, guarded clarification question when the quick rules allow it.
        """
        try:
            # lightweight import to avoid hard dependency on clarification internals
            from core.clarification.quick import quick_clarify
            from core.clarification.llm_questioner import ask
        except Exception:
            return {"decision": "fallback", "notes": ["clarification unavailable"]}

        context = situation.get("context", {})
        state = situation.get("state", {})

        plan = quick_clarify(context, state)
        if not plan:
            return {"decision": "no_clarification_needed"}

        # ask one question (blocking) and record answer in context.notes
        q = ask(plan, context)
        try:
            print(f"[Quick Clarification]: {q}")
            a = input("> ")
        except Exception:
            a = ""

        context.setdefault("notes", []).append(a)

        # do not reopen debate; return short summary
        return {"decision": "clarified", "question": q, "answer": a}
