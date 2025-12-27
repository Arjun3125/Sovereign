"""Simple per-minister retrieval helper.

Provides `retrieve_for_minister` which loads book metadata and returns
the top-N books for a given minister and mode using `MinisterRAGSelector`.
"""
from core.rag.minister_rag_selector import MinisterRAGSelector
from core.knowledge.book_metadata_loader import BookMetadataLoader


def retrieve_for_minister(minister_name, context=None, mode="standard", cap=5):
    """Return a ranked list of book metadata dicts for the minister.

    Args:
        minister_name: Friendly minister name (e.g., 'Psychology')
        context: Optional retrieval context (currently unused)
        mode: Retrieval mode, e.g., 'war' or 'standard'
        cap: Maximum number of books to return

    Returns:
        List[dict] of book metadata (ranked)
    """
    loader = BookMetadataLoader()
    all_meta = loader.load_all()

    # Convert mapping to list of metadata dicts
    books = list(all_meta.values())

    selector = MinisterRAGSelector()
    ranked = selector.select(minister_name, books, mode)

    return ranked[:cap]
