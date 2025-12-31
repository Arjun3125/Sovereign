from typing import Dict, Any

try:
    from core.llm import call_llm
except Exception:
    call_llm = None

SYSTEM = """You are framing ONE concise, neutral question.
Do not advise. Do not interpret. Ask only.
Return a single-line question only.
"""


def ask(plan: Dict[str, Any], context: Dict[str, Any]) -> str:
    hint = plan.get("prompt_hint", "")
    goal = plan.get("goal", "clarify")
    raw = (context.get("raw_text") if isinstance(context, dict) else str(context)) or ""

    user = f"Context excerpt: {raw[:800]}\nGoal: {goal}\nHint: {hint}\nAsk one concise question."

    if call_llm is not None:
        try:
            out = call_llm(system=SYSTEM, user=user)
            return out.strip().splitlines()[0]
        except Exception:
            pass

    # Fallback deterministic phrasing
    if hint:
        return f"Please clarify: {hint}. What key detail should we know?"
    return f"Please clarify the goal: {goal}. What important detail is missing?"
