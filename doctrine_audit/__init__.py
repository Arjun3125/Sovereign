from query_engine.loader import load_book
from .detect import detect_conflicts
from .report import format_report


def audit_book(book_id: str):
    """Audit a book for doctrine contradictions.
    
    Args:
        book_id: The book ID to audit (must be already ingested).
        
    Returns:
        Formatted report string.
    """
    chapters = load_book(book_id)
    conflicts = detect_conflicts(chapters)
    return format_report(conflicts)
