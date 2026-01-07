"""
Ingestion v2: Two-Pass Doctrine Compiler (MVP)

Phase-1: Whole Book → Canonical Chapters (LLM)
Phase-2: Each Chapter → Doctrine (LLM, per-chapter)
Phase-3: Extract Principles → Individual Files
Phase-4: Generate Embeddings
Phase-5: Seal with MANIFEST.json

MVP Folder Structure:
- raw_text.json (immutable)
- chapters.json (from Phase-1)
- principles/ (individual JSON files)
- embeddings/ (vector store)
- MANIFEST.json (completion seal)
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from .pdf_reader import extract_text
from .phase1_structure import phase1_structure
from .phase2_doctrine import phase2_doctrine
from .progress_v2 import Progress
from .llm_client import LLMError
from .validators_v2 import validate_phase1, validate_phase2, ValidationError
from .storage import (
    ensure_book_structure, save_raw_text, save_chapters,
    save_principle, save_manifest, is_book_sealed, load_manifest
)
from .principle_extractor import extract_principles_from_doctrine


def ingest_book(
    pdf_path: str,
    book_id: str,
    title: Optional[str] = None,
    authors: Optional[List[str]] = None,
    model_phase1: Optional[str] = None,
    model_phase2: Optional[str] = None,
    output_dir: str = "v2_store",
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Ingest a book using v2 two-pass compiler (MVP).
    
    Produces:
    - raw_text.json (immutable)
    - chapters.json (from Phase-1)
    - principles/*.json (individual principle files)
    - embeddings/ (vector store)
    - MANIFEST.json (completion seal)

    Args:
        pdf_path: Path to PDF file (or .txt file)
        book_id: Unique book identifier
        title: Book title (if None, extracted from filename)
        authors: List of author names (optional)
        model_phase1: Phase-1 LLM model (default: env OLLAMA_MODEL)
        model_phase2: Phase-2 LLM model (default: env OLLAMA_MODEL)
        output_dir: Root output directory (default: v2_store)

    Returns:
        {
            "book_id": str,
            "title": str,
            "chapters_count": int,
            "principles_count": int,
            "status": "DONE",
            "manifest_path": str
        }
    """
    print(f"\n[INGEST_V2] Starting ingestion for book: {book_id}")
    print(f"[INGEST_V2] PDF path: {pdf_path}")

    # Create MVP folder structure
    book_dir = ensure_book_structure(book_id, output_dir)
    
    # Check if already sealed and handle overwrite
    if is_book_sealed(book_dir) and not overwrite:
        manifest = load_manifest(book_dir)
        print(f"[INGEST_V2] Book already sealed (status: {manifest.get('status')})")
        print(f"[INGEST_V2] Use overwrite=True to re-ingest")
        return {
            "book_id": book_id,
            "title": manifest.get("title", ""),
            "chapters_count": manifest.get("chapters", 0),
            "principles_count": manifest.get("principles", 0),
            "status": "SEALED",
            "manifest_path": str(book_dir / "MANIFEST.json")
        }
    
    # Delete existing data if overwrite requested
    if overwrite:
        import shutil
        print(f"\n[OVERWRITE] Deleting existing ingestion data...")
        
        # Delete book directory if exists
        if book_dir.exists():
            print(f"[OVERWRITE] Removing: {book_dir}")
            try:
                shutil.rmtree(book_dir)
                print(f"[OVERWRITE] [OK] Deleted book directory")
            except Exception as e:
                print(f"[OVERWRITE] [FAIL] Failed to delete book directory: {e}")
                raise
        
        # Delete old YAML file if exists
        from .persist_book import BASE
        yaml_path = BASE / f"{book_id}.yaml"
        if yaml_path.exists():
            print(f"[OVERWRITE] Removing old YAML: {yaml_path}")
            try:
                yaml_path.unlink()
                print(f"[OVERWRITE] [OK] Deleted old YAML file")
            except Exception as e:
                print(f"[OVERWRITE] [WARN] Could not delete YAML: {e}")
        
        # Recreate directory structure
        book_dir = ensure_book_structure(book_id, output_dir)
        print(f"[OVERWRITE] Starting fresh ingestion...")

    # ============ STEP 0: EXTRACT TEXT ============
    print("\n" + "="*70)
    print("[STEP 0] Extracting text from PDF...")
    print("="*70)
    try:
        book_text = extract_text(pdf_path)
        if not book_text or len(book_text.strip()) < 100:
            raise ValueError(f"Extracted text too short ({len(book_text)} chars). Check PDF extraction.")
        print(f"[STEP 0] [OK] Extracted {len(book_text):,} characters | 100% complete")
        
        # Save raw text (immutable)
        save_raw_text(book_dir, book_text)
        print(f"[STEP 0] Saved raw_text.json")
    except Exception as e:
        print(f"[STEP 0] [FAIL] Failed to extract text: {e}")
        raise

    # ============ PHASE-1: BOOK STRUCTURING ============
    print("\n" + "="*70)
    print("[PHASE-1] Starting Phase-1 (Book Structuring)...")
    print("="*70)
    
    structure_path = book_dir / "chapters.json"
    structure = None
    
    # Check if structure already exists (resume-safe)
    if structure_path.exists():
        print(f"[PHASE-1] Structure already exists, loading from disk...")
        with open(structure_path, "r", encoding="utf-8") as f:
            chapters_data = json.load(f)
        chapters = chapters_data.get("chapters", [])
        num_chapters = len(chapters)
        print(f"[PHASE-1] Loaded {num_chapters} chapters from existing structure")
        # Build structure dict for later use
        structure = {
            "book_title": title or Path(pdf_path).stem,
            "author": authors[0] if authors and len(authors) == 1 else None,
            "chapters": chapters
        }
    else:
        print(f"[PHASE-1] Input: {len(book_text):,} characters")
        print(f"[PHASE-1] Step 1/3: Preparing prompt...")
        print(f"[PHASE-1] Step 2/3: Calling LLM to extract chapters...")
        try:
            structure = phase1_structure(book_text, model=model_phase1)
            print(f"[PHASE-1] Step 3/3: Validating structure...")
            validate_phase1(structure)
            
            chapters = structure["chapters"]
            num_chapters = len(chapters)
            
            # Update title/author if provided
            if title:
                structure["book_title"] = title
            if authors:
                structure["author"] = authors[0] if len(authors) == 1 else None
            
            # Save chapters
            print(f"[PHASE-1] Saving chapters to disk...")
            save_chapters(book_dir, chapters)
            print(f"[PHASE-1] Structure saved to {structure_path}")
        except (LLMError, ValidationError) as e:
            print(f"[PHASE-1] [FAIL] Failed: {e}")
            raise

    # Initialize progress tracker
    prog = Progress(num_chapters)
    prog.phase1_complete()

    # ============ PHASE-2: DOCTRINE EXTRACTION ============
    print("\n" + "="*70)
    print(f"[PHASE-2] Starting Phase-2 (Doctrine Extraction)...")
    print("="*70)
    prog.phase2_start()

    ingested_count = 0
    skipped_count = 0
    failed_count = 0
    all_doctrine = []

    for ch in chapters:
        chapter_idx = ch["chapter_index"]
        chapter_title = ch["chapter_title"]
        chapter_path = book_dir / f"{chapter_idx:02d}.json"

        # Check if already ingested (resume-safe)
        if chapter_path.exists():
            with open(chapter_path, "r", encoding="utf-8") as f:
                doctrine = json.load(f)
            all_doctrine.append(doctrine)
            skipped_count += 1
            prog.chapter_skipped(chapter_idx, chapter_title)
            continue

        try:
            # Extract doctrine
            print(f"[PHASE-2] Chapter {chapter_idx}: Step 1/3 - Preparing prompt...")
            print(f"[PHASE-2] Chapter {chapter_idx}: Step 2/3 - Calling LLM...")
            doctrine = phase2_doctrine(ch, model=model_phase2)
            print(f"[PHASE-2] Chapter {chapter_idx}: Step 3/3 - Validating doctrine...")
            validate_phase2(doctrine)

            # Save doctrine immutably
            print(f"[PHASE-2] Chapter {chapter_idx}: Saving to disk...")
            with open(chapter_path, "w", encoding="utf-8") as f:
                json.dump(doctrine, f, indent=2, ensure_ascii=False)

            all_doctrine.append(doctrine)
            ingested_count += 1
            prog.chapter_ingested(chapter_idx, chapter_title)

        except (LLMError, ValidationError) as e:
            print(f"[PHASE-2] [FAIL] Chapter {chapter_idx} extraction failed: {e}")
            print(f"        Will retry on next run (resume-safe)")
            failed_count += 1
            all_doctrine.append(None)

    prog.complete()

    # Print Phase-2 summary
    print(f"\n[PHASE-2] Summary:")
    print(f"  - Ingested: {ingested_count} chapters")
    print(f"  - Skipped (already existed): {skipped_count} chapters")
    if failed_count > 0:
        print(f"  - Failed (will retry): {failed_count} chapters")

    # ============ PHASE-3: PRINCIPLE EXTRACTION ============
    print("\n" + "="*70)
    print("[PHASE-3] Extracting principles from doctrine...")
    print("="*70)
    
    all_principles = []
    for ch, doctrine in zip(chapters, all_doctrine):
        if doctrine is None:
            continue
        
        chapter_id = str(ch["chapter_index"])
        principles = extract_principles_from_doctrine(doctrine, book_id, chapter_id)
        
        # Save each principle as individual file
        for principle in principles:
            save_principle(book_dir, principle)
            all_principles.append(principle)
    
    print(f"[PHASE-3] [OK] Extracted {len(all_principles)} principles")
    print(f"[PHASE-3] Saved {len(all_principles)} individual principle files")

    # ============ PHASE-4: EMBEDDINGS (Placeholder) ============
    print("\n" + "="*70)
    print("[PHASE-4] Generating embeddings...")
    print("="*70)
    print(f"[PHASE-4] Embedding generation will be implemented next")
    print(f"[PHASE-4] Principles ready for embedding: {len(all_principles)}")
    # TODO: Implement embedding generation
    # embeddings_dir = book_dir / "embeddings"
    # for principle in all_principles:
    #     embedding = embed(principle["text"])
    #     save_embedding(embeddings_dir, principle["id"], embedding)

    # ============ PHASE-5: SEAL WITH MANIFEST ============
    print("\n" + "="*70)
    print("[PHASE-5] Sealing book with MANIFEST.json...")
    print("="*70)
    
    manifest = {
        "book_id": book_id,
        "title": structure.get("book_title", title or Path(pdf_path).stem),
        "status": "DONE",
        "chapters": num_chapters,
        "principles": len(all_principles),
        "ingestion_mode": "chapter_based",
        "ingested_at": None,  # TODO: Add timestamp
        "reingest_allowed": False
    }
    
    save_manifest(book_dir, manifest)
    print(f"[PHASE-5] [OK] Book sealed | MANIFEST.json created")
    print(f"[PHASE-5] Status: DONE | Principles: {len(all_principles)}")

    print(f"\n[INGEST_V2] [OK] Ingestion complete!")
    print(f"[INGEST_V2] Book ID: {book_id}")
    print(f"[INGEST_V2] Chapters: {num_chapters}")
    print(f"[INGEST_V2] Principles: {len(all_principles)}")
    print(f"[INGEST_V2] Output: {book_dir}")

    return {
        "book_id": book_id,
        "title": manifest["title"],
        "chapters_count": num_chapters,
        "principles_count": len(all_principles),
        "status": "DONE",
        "manifest_path": str(book_dir / "MANIFEST.json")
    }
