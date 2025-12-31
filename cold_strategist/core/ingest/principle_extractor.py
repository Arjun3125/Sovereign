from typing import Dict, Any, List
import json
import pathlib
try:
    from core.llm.gateway import call_llm
except Exception:
    call_llm = None

SYSTEM = """Extract CLAIMED principles only. No advice. Include conditions/counter-conditions.
Return strict JSON object: {"principle":..., "conditions":[], "counter_conditions":[], "evidence_type":...}
"""


def extract_principles(semantic: Dict[str, Any], out_dir: str = None, profile: str = "default") -> Dict[str, Any]:
    slices = semantic.get("slices", [])
    principles: List[Dict] = []
    for s in slices:
        text = s.get("text", "")
        result = None
        if call_llm is not None:
            try:
                # Use task-based model routing for principle extraction
                resp = call_llm(system=SYSTEM, user=text, task="principle_extraction")
                # Diagnostic: print raw LLM response
                try:
                    print("RAW_LLM_RESPONSE_START")
                    print(resp)
                    print("RAW_LLM_RESPONSE_END")
                except Exception:
                    pass
                result = json.loads(resp)
            except Exception:
                result = None

        if result is None:
            # Fallback: simple heuristic—take first sentence as claimed principle
            import re
            sent = re.split(r"(?<=[.!?])\\s+", text.strip())
            principle_text = sent[0].strip() if sent else text.strip()
            result = {"principle": principle_text, "conditions": [], "counter_conditions": [], "evidence_type": "textual"}

        result["derived_from"] = s.get("id") or s.get("slice_id")
        result["profile"] = profile
        principles.append(result)

    out = {"book_id": semantic.get("book_id"), "principles": principles}
    if out_dir:
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{out_dir}/{out['book_id']}.json", "w", encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    # Diagnostic: report how many principle objects we produced
    try:
        print("DEBUG: extracted principles count =", len(principles))
        print("EXTRACTOR_COUNT", len(principles))
    except Exception:
        pass

    return out
