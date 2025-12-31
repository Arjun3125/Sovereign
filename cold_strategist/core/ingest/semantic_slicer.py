import json
import pathlib
from typing import Dict, Any, List
try:
    from core.llm import call_llm
except Exception:
    call_llm = None


SYSTEM = """Slice ONLY. Do not summarize or interpret.
Return coherent idea units preserving stories/analogies.
Output JSON list: [{"id","type","text","notes"}]
"""


def semantic_slice(structural_json: Dict[str, Any], out_dir: str = None, llm_guarded: bool = True) -> Dict[str, Any]:
    """LLM-guarded slicing. If `core.llm.call_llm` exists, use it; otherwise fall back to paragraph heuristics."""
    sections = structural_json.get("sections", [])
    slices = []

    for sec in sections:
        sec_text = sec.get("text", "")
        units = None
        if llm_guarded and call_llm is not None:
            try:
                resp = call_llm(system=SYSTEM, user=f"SECTION:\n{sec_text}")
                units = json.loads(resp)
            except Exception:
                units = None

        if units is None:
            # heuristic: split on double newlines into idea units
            paras = [p.strip() for p in sec_text.split('\n\n') if p.strip()]
            units = [{"id": f"{structural_json.get('book_id')}_slice_{i+1}", "type": "idea", "text": p, "notes": "heuristic"} for i, p in enumerate(paras)]

        for u in units:
            u.setdefault("chapter", sec.get("chapter"))
            slices.append(u)

    out = {"book_id": structural_json.get("book_id"), "slices": slices}
    if out_dir:
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{out_dir}/{out['book_id']}.json", "w", encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    return out
