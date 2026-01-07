"""
End-to-end ingestion pipeline.

PDF → text → structural chunking → semantic slicing → metadata binding → indexing
"""

from pathlib import Path
from core.knowledge.ingest import extract_pdf, structural_chunker, semantic_slicer, metadata_binder, indexer
from core.knowledge.registry import get_book_config
from rag.index import VectorIndex


def simple_embed(text: str):
    """Placeholder embed: char ordinal mean."""
    if not text:
        return [0.0] * 3
    vals = [float(ord(c)) for c in text[:256]]
    mean = sum(vals) / len(vals) if vals else 0.0
    return [mean % 1.0, (mean*2) % 1.0, (mean*3) % 1.0]


def ingest_book(book_id: str, book_dir: str, index: VectorIndex, llm_fn=None) -> int:
    """
    Ingest a book through the complete pipeline.
    
    Args:
        book_id: Identifier (e.g., "art_of_seduction")
        book_dir: Directory containing raw.txt (and optionally .pdf)
        index: VectorIndex to populate
        llm_fn: Optional LLM function for semantic slicing
        
    Returns:
        Number of chunks indexed
    """
    book_dir = Path(book_dir)
    if not book_dir.exists():
        raise FileNotFoundError(f"Book dir not found: {book_dir}")
    
    # Get book config (validates book_id and reads chapter markers)
    config = get_book_config(book_id)
    
    # Step 1: Extract text
    raw_file = book_dir / "raw.txt"
    if raw_file.exists():
        raw_text = raw_file.read_text(encoding='utf-8')
    else:
        # Try PDF
        pdf_file = book_dir / (book_id + ".pdf")
        try:
            raw_text = extract_pdf.extract_pdf_text(str(pdf_file))
        except FileNotFoundError:
            raw_text = ""
    
    if not raw_text:
        raise ValueError(f"No text found in {book_dir}")
    
    # Step 2: Structural chunking (deterministic, chapter-aware)
    chapters = config.get("chapters", [])
    sections = structural_chunker.split_by_structure(raw_text, chapters)
    
    total_chunks = 0
    
    # Step 3-6: For each section, slice, tag, and index
    for section in sections:
        chapter = section["chapter"]
        section_text = section["raw_text"]
        
        # Semantic slicing (may use LLM for split points, not summarization)
        chunks = semantic_slicer.slice_for_retrieval(section_text, llm_fn=llm_fn)
        
        # Metadata binding (add domains, minister permissions)
        enriched = [
            metadata_binder.bind_metadata(
                c,
                book_id=book_id,
                chapter=chapter,
                domains=config.get("domains", []),
                allowed_ministers=config.get("allowed_ministers", [])
            )
            for c in chunks
        ]
        
        # Indexing (vector + payload)
        indexer.index_chunks(enriched, simple_embed, index)
        total_chunks += len(enriched)
    
    return total_chunks


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ingest_pipeline.py <book_id> [book_dir]")
        print("Example: python ingest_pipeline.py art_of_seduction rag/books/art_of_seduction")
        sys.exit(1)
    
    book_id = sys.argv[1]
    book_dir = sys.argv[2] if len(sys.argv) > 2 else f"rag/books/{book_id}"
    
    index = VectorIndex(simple_embed)
    
    try:
        count = ingest_book(book_id, book_dir, index)
        print(f"✓ Ingestion complete: {count} chunks indexed for {book_id}")
    except Exception as e:
        print(f"✗ Ingestion failed: {e}")
        sys.exit(1)
