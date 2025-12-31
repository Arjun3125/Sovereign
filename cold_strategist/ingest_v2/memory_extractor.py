"""Memory extractor (deterministic fallback for Prompt 2).

This module provides a deterministic, rule-based memory extractor to
implement the PROMPT 2 behavior without requiring a live LLM. It is
intended for fast local testing and to validate parsing/persistence
paths. The function `extract_memory_items` returns the strict JSON
shape required by the pipeline.
"""
from typing import Dict, List, Optional
import re
from .llm_utils import extract_json_block

DOMAIN_KEYWORDS = {
    "grand_strategy": ["grand", "strategy", "strategic"],
    "power": ["power", "authority", "dominate", "influence"],
    "optionality": ["option", "optional", "flexib", "choice"],
    "psychology": ["psych", "mind", "morale", "belief"],
    "diplomacy": ["diplom", "treaty", "ally", "negotiat"],
    "conflict": ["conflict", "battle", "fight", "combat"],
    "truth": ["truth", "fact", "real"],
    "risk": ["risk", "danger", "hazard", "exposure"],
    "timing": ["time", "timing", "speed", "delay"],
    "data_judgment": ["data", "evidence", "judg", "estimate"],
    "operations": ["operat", "logist", "supply", "execution"],
    "technology": ["tech", "technology", "mechan", "system"],
    "adaptation": ["adapt", "adjust", "evolve", "flex"],
    "legitimacy": ["legit", "authority", "mandate", "consent"],
    "narrative": ["narrative", "story", "frame", "message"],
}


def _sentences(text: str) -> List[str]:
    # Split on sentence boundaries; keep short trimming.
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    out = [p.strip() for p in parts if p and len(p.strip()) > 10]
    return out


def _matches_sentence_for_domain(sent: str, domain: str) -> bool:
    kws = DOMAIN_KEYWORDS.get(domain, [])
    s = sent.lower()
    for k in kws:
        if k in s:
            return True
    return False


def extract_memory_items(chapter: Dict, domain: str, max_items: int = 6) -> Dict:
    """Extract memory-grade items for a single (chapter, domain) pair.

    Returns a dict matching the PROMPT 2 expected JSON shape:
    {"chapter_id": "..", "domain": "..", "memory_items": [..]}

    The extraction is conservative: returns sentences that explicitly
    mention domain keywords. If none match, returns an empty list
    (as allowed by the prompt rules).
    """
    chapter_id = chapter.get("chapter_id") or chapter.get("id") or ""
    text = chapter.get("text", "")
    items: List[str] = []

    if not text or not domain:
        return {"chapter_id": chapter_id, "domain": domain, "memory_items": []}

    for sent in _sentences(text):
        if _matches_sentence_for_domain(sent, domain):
            # Keep sentence but normalize whitespace
            item = " ".join(sent.split())
            if item not in items:
                items.append(item)
            if len(items) >= max_items:
                break

    return {"chapter_id": chapter_id, "domain": domain, "memory_items": items}


def extract_for_pairs(pairs: List[Dict]) -> List[Dict]:
    """Helper to extract many (chapter, domain) pairs.

    Each dict in `pairs` should contain `chapter` and `domain` keys.
    Returns a list of result dicts in the PROMPT 2 shape.
    """
    out = []
    for p in pairs:
        chapter = p.get("chapter") or {}
        domain = p.get("domain") or ""
        out.append(extract_memory_items(chapter, domain))
    return out


def parse_memory_items_from_llm(text: str) -> Optional[List[str]]:
    """Extract `memory_items` list from noisy LLM output if present, else None."""
    if not text:
        return None
    try:
        data = extract_json_block(text)
        if isinstance(data, dict) and "memory_items" in data and isinstance(data["memory_items"], list):
            return data["memory_items"]
    except Exception:
        return None
    return None
