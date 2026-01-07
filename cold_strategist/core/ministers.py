import json
from pathlib import Path
from typing import Dict, Set

BASE_DIR = Path(__file__).resolve().parent.parent
MINISTER_DIR = BASE_DIR / "minister_constraints"


class MinisterConstraint:
    def __init__(self, data: dict):
        self.id = data["minister_id"]
        self.worldview = data["worldview"]
        self.forbidden = set(data.get("forbidden_concepts", []))
        self.allowed = set(data.get("allowed_focus", []))
        self.output_shape = data.get("output_shape", {})
        self.threshold = data.get("confidence_threshold", {})


def load_all_ministers() -> Dict[str, MinisterConstraint]:
    ministers: Dict[str, MinisterConstraint] = {}

    if not MINISTER_DIR.exists():
        raise RuntimeError(f"Minister directory not found: {MINISTER_DIR}")

    for file in MINISTER_DIR.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            m = MinisterConstraint(data)
            ministers[m.id] = m

    return ministers
