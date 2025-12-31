from typing import Dict, List, Any


def bind_metadata(
    chunk: Dict[str, Any],
    book_id: str,
    chapter: str,
    domains: List[str],
    allowed_ministers: List[str]
) -> Dict[str, Any]:
    """
    Bind metadata and minister permissions to a chunk.
    
    Args:
        chunk: Chunk dict with text, type
        book_id: Book identifier
        chapter: Chapter name
        domains: List of domain tags
        allowed_ministers: List of ministers with access
        
    Returns:
        Enriched chunk dict with metadata and permissions
    """
    return {
        **chunk,
        "book_id": book_id,
        "chapter": chapter,
        "domains": domains,
        "allowed_ministers": allowed_ministers,
        "source": {
            "book": book_id,
            "chapter": chapter,
        }
    }
