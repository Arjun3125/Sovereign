"""Main orchestrator for ingest_v2 pipeline.

This is the entry point for the new ingestion model. It orchestrates:
1. PDF/text reading
2. Chapter building
3. Domain classification
4. Memory extraction
5. Book aggregation
6. Persistence
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from .pdf_reader import extract_text
from .chapter_builder import build_chapters
from .domain_classifier import classify_chapter
from .memory_extractor import extract_memory_items
from .book_aggregator import aggregate
from .persist_book import persist
from .yaml_schema import validate_book, ValidationError


def ingest_book(
    pdf_path: str,
    book_id: str,
    title: Optional[str] = None,
    authors: Optional[List[str]] = None,
    use_llm: bool = False
) -> Dict[str, Any]:
    """Ingest a book using the v2 pipeline.
    
    Args:
        pdf_path: Path to PDF file (or .txt file)
        book_id: Unique book identifier
        title: Book title (if None, extracted from filename)
        authors: List of author names (optional)
        use_llm: If True, use LLM for domain classification and memory extraction
    
    Returns:
        Dict with ingestion results:
        {
            "book_id": str,
            "title": str,
            "chapters_count": int,
            "output_path": str,
            "status": "success" | "error"
        }
    
    Raises:
        FileNotFoundError: If PDF path doesn't exist
        ValidationError: If book structure validation fails
    """
    print(f"\n[INGEST_V2] Starting ingestion for book: {book_id}")
    print(f"[INGEST_V2] PDF path: {pdf_path}")
    
    # Step 1: Extract text from PDF
    print("\n[STEP 1] Extracting text from PDF...")
    try:
        book_text = extract_text(pdf_path)
        if not book_text or len(book_text.strip()) < 100:
            raise ValueError(f"Extracted text too short ({len(book_text)} chars). Check PDF extraction.")
        print(f"[STEP 1] [OK] Extracted {len(book_text)} characters")
    except Exception as e:
        print(f"[STEP 1] [FAIL] Failed to extract text: {e}")
        raise
    
    # Step 2: Build chapters
    print("\n[STEP 2] Building chapters...")
    try:
        chapters = build_chapters(book_text)
        if not chapters:
            raise ValueError("No chapters found in text")
        print(f"[STEP 2] [OK] Found {len(chapters)} chapters")
    except Exception as e:
        print(f"[STEP 2] [FAIL] Failed to build chapters: {e}")
        raise
    
    # Step 3: Classify domains for each chapter
    print("\n[STEP 3] Classifying domains...")
    domain_classifications = []
    for i, chapter in enumerate(chapters, 1):
        try:
            classification = classify_chapter(chapter, retries=1)
            domain_classifications.append(classification)
            domains = classification.get("domains", [])
            print(f"[STEP 3] Chapter {i}: {len(domains)} domains ({', '.join(domains[:3])}{'...' if len(domains) > 3 else ''})")
        except Exception as e:
            print(f"[STEP 3] [FAIL] Failed to classify chapter {i}: {e}")
            # Continue with empty domains
            domain_classifications.append({
                "chapter_id": chapter.get("chapter_id", str(i)),
                "domains": []
            })
    print(f"[STEP 3] [OK] Classified {len(domain_classifications)} chapters")
    
    # Step 4: Extract memory items for each (chapter, domain) pair
    print("\n[STEP 4] Extracting memory items...")
    memory_extractions = []
    total_pairs = 0
    for chapter in chapters:
        cid = chapter.get("chapter_id", "")
        # Find domains for this chapter
        classification = next(
            (dc for dc in domain_classifications if dc.get("chapter_id") == cid),
            None
        )
        domains = classification.get("domains", []) if classification else []
        
        for domain in domains:
            total_pairs += 1
            try:
                memory_result = extract_memory_items(chapter, domain, max_items=6)
                memory_extractions.append(memory_result)
                items_count = len(memory_result.get("memory_items", []))
                if items_count > 0:
                    print(f"[STEP 4] Chapter {cid}, {domain}: {items_count} memory items")
            except Exception as e:
                print(f"[STEP 4] [FAIL] Failed to extract memory for chapter {cid}, domain {domain}: {e}")
                # Continue with empty memory
                memory_extractions.append({
                    "chapter_id": cid,
                    "domain": domain,
                    "memory_items": []
                })
    print(f"[STEP 4] [OK] Processed {total_pairs} (chapter, domain) pairs")
    
    # Step 5: Aggregate book structure
    print("\n[STEP 5] Aggregating book structure...")
    try:
        if title is None:
            title = Path(pdf_path).stem.replace("_", " ").title()
        
        book_artifact = aggregate(
            book_id=book_id,
            title=title,
            authors=authors or [],
            chapters=chapters,
            domain_classifications=domain_classifications,
            memory_extractions=memory_extractions
        )
        print(f"[STEP 5] [OK] Aggregated {len(book_artifact['chapters'])} chapters")
    except Exception as e:
        print(f"[STEP 5] [FAIL] Failed to aggregate: {e}")
        raise
    
    # Step 6: Validate structure
    print("\n[STEP 6] Validating book structure...")
    try:
        validate_book(book_artifact)
        print(f"[STEP 6] [OK] Validation passed")
    except ValidationError as e:
        print(f"[STEP 6] [FAIL] Validation failed: {e}")
        raise
    
    # Step 7: Persist to YAML
    print("\n[STEP 7] Persisting book to YAML...")
    try:
        output_path = persist(book_id, book_artifact)
        print(f"[STEP 7] [OK] Saved to: {output_path}")
    except FileExistsError as e:
        print(f"[STEP 7] [WARN] Book already exists: {e}")
        # Return existing path
        from .persist_book import BASE
        output_path = str(BASE / f"{book_id}.yaml")
    except Exception as e:
        print(f"[STEP 7] [FAIL] Failed to persist: {e}")
        raise
    
    print(f"\n[INGEST_V2] [OK] Ingestion complete!")
    print(f"[INGEST_V2] Book ID: {book_id}")
    print(f"[INGEST_V2] Chapters: {len(chapters)}")
    print(f"[INGEST_V2] Output: {output_path}")
    
    return {
        "book_id": book_id,
        "title": book_artifact["title"],
        "chapters_count": len(chapters),
        "output_path": output_path,
        "status": "success"
    }

