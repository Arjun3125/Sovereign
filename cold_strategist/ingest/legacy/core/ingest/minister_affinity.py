import json
import pathlib
from typing import Dict, Any, List

RULES = {
    "Psychology": ["bias", "emotion", "persuasion", "seduction", "charm"],
    "Power": ["leverage", "status", "dominance", "reputation"],
    "Conflict": ["force", "escalation", "deterrence", "war", "attack"],
}


def tag(principles_json: Dict[str, Any], out_dir: str = None, war_weight: float = 0.5) -> Dict[str, Any]:
    data = principles_json
    tagged = []
    for p in data.get("principles", []):
        text = p.get("principle", "").lower()
        affinity = [m for m, kws in RULES.items() if any(k in text for k in kws)]
        if not affinity:
            affinity = ["General"]

        tagged.append({
            "principle_id": p.get("principle_id") or p.get("derived_from"),
            "affinity": affinity,
            "war_weight": war_weight,
        })

    out = {"book_id": data.get("book_id"), "affinity": tagged}
    if out_dir:
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{out_dir}/{out['book_id']}.json", "w", encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    return out
