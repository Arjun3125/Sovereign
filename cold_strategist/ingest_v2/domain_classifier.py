"""Domain classifier (LLM #1) — minimal keyword-based classifier with retry control.
In production this would call an LLM; here we use deterministic keyword matching.
"""
from typing import Dict, List, Optional
from .schemas import DOMAIN_LIST
from .retry_controller import retry
from .llm_utils import extract_json_block


KEYWORDS = {
    "power": ["power", "influence", "authority", "dominance"],
    "strategy": ["strategy", "strategic", "plan", "tactic"],
    "diplomacy": ["diplom", "ally", "negotiat", "treaty"],
    "economy": ["econom", "resource", "supply", "cost"],
    "timing": ["time", "timing", "speed", "delay"],
}


def _classify_text(text: str) -> List[str]:
    found = set()
    t = text.lower()
    for d in DOMAIN_LIST:
        kws = KEYWORDS.get(d, [])
        for k in kws:
            if k in t:
                found.add(d)
                break
    # Ensure at least one domain
    if not found:
        return [DOMAIN_LIST[0]]
    return list(found)


def classify_chapter(chapter: Dict, retries: int = 1) -> Dict:
    """Return dict: {chapter_id, domains: [...]}

    Retries are performed by re-running the deterministic classifier (keeps policy shape).
    """
    func = lambda: {"chapter_id": chapter["chapter_id"], "domains": _classify_text(chapter.get("text", ""))}
    if retries > 0:
        f = retry(func, retries=retries, delay=0.2)
        return f()
    return func()


def parse_domains_from_llm(text: str) -> Optional[List[str]]:
    """Try to extract a domains list from noisy LLM output using JSON extraction.

    Returns list of domains or None if parsing fails.
    """
    if not text:
        return None
    try:
        data = extract_json_block(text)
        if isinstance(data, dict) and "domains" in data and isinstance(data["domains"], list):
            return data["domains"]
    except Exception:
        return None
    return None
