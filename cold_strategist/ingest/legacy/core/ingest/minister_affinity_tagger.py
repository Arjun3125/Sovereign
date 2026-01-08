from typing import Dict, Any, List
import re


KEYWORD_TO_MINISTER = {
    "power": ["power"],
    "psychology": ["charm", "psycholog", "emotion", "perception"],
    "diplomacy": ["diplomacy", "negotia", "treaty", "dialogue"],
    "conflict": ["war", "battle", "fight", "escalat"],
}


def tag_affinity(principles_doc: Dict[str, Any], war_shelf: bool = False) -> Dict[str, Any]:
    principles = principles_doc.get("principles", [])
    affinities: List[Dict] = []
    for p in principles:
        text = p.get("principle", "").lower()
        aff = []
        for minister, kws in KEYWORD_TO_MINISTER.items():
            for kw in kws:
                if kw in text:
                    aff.append(minister)
                    break
        if not aff:
            aff = ["strategy"]

        war_weight = 0.5
        if war_shelf and any(k in text for k in ["war", "battle", "attack", "escalat"]):
            war_weight = 0.9

        affinities.append({
            "principle_id": p.get("principle_id"),
            "affinity": [a.capitalize() for a in aff],
            "war_weight": war_weight,
        })

    return {"book_id": principles_doc.get("book_id"), "affinities": affinities}
