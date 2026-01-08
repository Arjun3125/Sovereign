import json
import statistics as stats
from typing import Dict, Any


def build_report(book_id: str, raw: Dict[str, Any], structural: Dict[str, Any], semantic: Dict[str, Any], principles: Dict[str, Any], affinity: Dict[str, Any]) -> Dict[str, Any]:
    slices = semantic.get("slices", []) if semantic else []
    principles_list = principles.get("principles", []) if principles else []
    affinity_list = affinity.get("affinity", []) if affinity else []

    slice_lengths = [len(s.get("text", "")) for s in slices] if slices else [0]

    return {
        "book_id": book_id,
        "counts": {
            "pages": len(raw.get("pages", [])),
            "sections": len(structural.get("sections", [])),
            "slices": len(slices),
            "principles": len(principles_list),
            "affinity_links": len(affinity_list),
        },
        "slice_lengths": {
            "min": min(slice_lengths),
            "avg": int(stats.mean(slice_lengths)) if slice_lengths else 0,
            "max": max(slice_lengths),
        },
        "warnings": [],
        "status": "ok",
    }


def add_warning(report: Dict[str, Any], msg: str) -> None:
    report.setdefault("warnings", []).append(msg)
