"""Aggregate book artifacts for ingest_v2.

Combines chapters, domain classifications, and memory extractions into
a single book artifact structure ready for persistence.
"""
from typing import Dict, List, Any


def aggregate(
    book_id: str,
    title: str,
    authors: List[str],
    chapters: List[Dict],
    domain_classifications: List[Dict],
    memory_extractions: List[Dict]
) -> Dict[str, Any]:
    """Aggregate all book artifacts into a single structure.
    
    Args:
        book_id: Unique book identifier
        title: Book title
        authors: List of author names (can be empty)
        chapters: List of chapter dicts with {chapter_id, title, text}
        domain_classifications: List of {chapter_id, domains: [...]}
        memory_extractions: List of {chapter_id, domain, memory_items: [...]}
    
    Returns:
        Aggregated book structure ready for YAML persistence
    """
    # Create a map of chapter_id -> chapter data
    chapter_map = {ch["chapter_id"]: ch for ch in chapters}
    
    # Create a map of chapter_id -> domains
    domain_map = {}
    for dc in domain_classifications:
        cid = dc.get("chapter_id")
        if cid:
            domain_map[cid] = dc.get("domains", [])
    
    # Create a map of (chapter_id, domain) -> memory_items
    memory_map = {}
    for me in memory_extractions:
        cid = me.get("chapter_id")
        domain = me.get("domain")
        if cid and domain:
            key = (cid, domain)
            memory_map[key] = me.get("memory_items", [])
    
    # Build the aggregated structure
    aggregated_chapters = []
    for chapter in chapters:
        cid = chapter["chapter_id"]
        domains = domain_map.get(cid, [])
        
        # Build memory list for this chapter
        chapter_memory = []
        for domain in domains:
            key = (cid, domain)
            memory_items = memory_map.get(key, [])
            if memory_items:  # Only include domains with memory items
                chapter_memory.append({
                    "domain": domain,
                    "memory_items": memory_items
                })
        
        aggregated_chapters.append({
            "chapter_id": cid,
            "title": chapter.get("title", ""),
            "domains": domains,
            "memory": chapter_memory
        })
    
    return {
        "book_id": book_id,
        "title": title,
        "authors": authors if authors else [],
        "chapters": aggregated_chapters
    }
