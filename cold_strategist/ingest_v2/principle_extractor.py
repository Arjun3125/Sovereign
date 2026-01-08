"""
Principle extraction from chapter doctrine.

Converts Phase-2 doctrine output into individual principle objects
following the MVP schema.
"""
from typing import Dict, List, Any


def extract_principles_from_doctrine(
    doctrine: Dict,
    book_id: str,
    chapter_id: str
) -> List[Dict]:
    """
    Extract individual principles from Phase-2 doctrine output.
    
    Args:
        doctrine: Phase-2 output with principles, rules, claims, warnings
        book_id: Book identifier
        chapter_id: Chapter identifier (e.g., "ch_01" or chapter_index)
    
    Returns:
        List of principle objects following MVP schema
    """
    principles = []
    principle_counter = 1
    
    # Extract from principles field
    for item in doctrine.get("principles", []):
        if isinstance(item, str) and item.strip():
            # Handle chapter_id as string or int
            ch_id = str(chapter_id).zfill(2) if chapter_id else "00"
            principle_id = f"{book_id}_p_{ch_id}_{principle_counter:03d}"
            principles.append({
                "id": principle_id,
                "text": item.strip(),
                "source_book": book_id,
                "chapter_id": chapter_id,
                "chapter_title": doctrine.get("chapter_title", ""),
                "type": "principle",
                "confidence": 0.85,  # Default confidence
                "tags": doctrine.get("domains", [])
            })
            principle_counter += 1
    
    # Extract from rules field
    for item in doctrine.get("rules", []):
        if isinstance(item, str) and item.strip():
            ch_id = str(chapter_id).zfill(2) if chapter_id else "00"
            principle_id = f"{book_id}_p_{ch_id}_{principle_counter:03d}"
            principles.append({
                "id": principle_id,
                "text": item.strip(),
                "source_book": book_id,
                "chapter_id": chapter_id,
                "chapter_title": doctrine.get("chapter_title", ""),
                "type": "rule",
                "confidence": 0.90,  # Rules are more concrete
                "tags": doctrine.get("domains", [])
            })
            principle_counter += 1
    
    # Extract from claims field
    for item in doctrine.get("claims", []):
        if isinstance(item, str) and item.strip():
            ch_id = str(chapter_id).zfill(2) if chapter_id else "00"
            principle_id = f"{book_id}_p_{ch_id}_{principle_counter:03d}"
            principles.append({
                "id": principle_id,
                "text": item.strip(),
                "source_book": book_id,
                "chapter_id": chapter_id,
                "chapter_title": doctrine.get("chapter_title", ""),
                "type": "claim",
                "confidence": 0.80,  # Claims are more interpretive
                "tags": doctrine.get("domains", [])
            })
            principle_counter += 1
    
    # Extract from warnings field
    for item in doctrine.get("warnings", []):
        if isinstance(item, str) and item.strip():
            ch_id = str(chapter_id).zfill(2) if chapter_id else "00"
            principle_id = f"{book_id}_p_{ch_id}_{principle_counter:03d}"
            principles.append({
                "id": principle_id,
                "text": item.strip(),
                "source_book": book_id,
                "chapter_id": chapter_id,
                "chapter_title": doctrine.get("chapter_title", ""),
                "type": "warning",
                "confidence": 0.85,
                "tags": doctrine.get("domains", [])
            })
            principle_counter += 1
    
    return principles

