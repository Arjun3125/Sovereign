from typing import List, Dict, Any


class ShelfBuilder:
    def __init__(self, index):
        self.index = index

    def build_for_minister(self, minister: str, war: bool = False) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for book_id, data in (self.index.books or {}).items():
            affinity_doc = data.get("affinity") or {}
            affinities = affinity_doc.get("affinity") if isinstance(affinity_doc, dict) else affinity_doc
            if not affinities:
                affinities = []
            for a in affinities:
                aff_list = a.get("affinity") if isinstance(a, dict) else a
                if not aff_list:
                    continue
                # match minister (case-insensitive)
                matches = [m for m in aff_list if m.lower() == minister.lower() or minister.lower() == "general"]
                if matches:
                    weight = float(a.get("war_weight", 0.5))
                    if war:
                        weight = weight * 1.3
                    items.append({
                        "book": book_id,
                        "principles": data.get("principles", {}).get("principles") or [],
                        "weight": weight,
                    })
        return items
