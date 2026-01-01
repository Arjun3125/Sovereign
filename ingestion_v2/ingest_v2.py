"""
Ingestion v2: Main orchestrator.

Two-pass doctrine compiler:
  Phase-1: Whole book → canonical chapters (LLM)
  Phase-2: Each chapter → doctrine (LLM, parallel-ready)

Resume-safe, progress-tracked, schema-hardened.
"""

import os
import json
from .phase1_structure import phase1_structure
from .phase2_doctrine import phase2_doctrine
from .progress import Progress
from .llm_client import LLMError
from .validators import ValidationError


def ingest_v2(book_text: str, book_id: str, output_dir: str = "v2_store", model_phase1: str = None, model_phase2: str = None) -> dict:
    """
    Ingest a book using v2 two-pass compiler.

    Args:
        book_text: Full book text
        book_id: Unique book identifier (used for storage)
        output_dir: Root output directory (default: v2_store)
        model_phase1: Phase-1 LLM model (default: env OLLAMA_MODEL)
        model_phase2: Phase-2 LLM model (default: env OLLAMA_MODEL)

    Returns:
        {
            "book_id": str,
            "structure_path": str,
            "chapters_ingested": int,
            "output_dir": str
        }

    Raises:
        LLMError: If any LLM call fails
        ValidationError: If schema validation fails
    """
    book_dir = os.path.join(output_dir, book_id)
    os.makedirs(book_dir, exist_ok=True)

    structure_path = os.path.join(book_dir, "structure.json")

    # ============ PHASE-1 ============
    print(f"\n[INGESTION] Starting Phase-1 (Book Structuring)...")

    structure = phase1_structure(book_text, model=model_phase1)
    chapters = structure["chapters"]

    # Save structure
    with open(structure_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)

    print(f"[INGESTION] Phase-1 complete: {len(chapters)} chapters extracted")

    # ============ PHASE-2 ============
    print(f"\n[INGESTION] Starting Phase-2 (Doctrine Extraction)...")

    prog = Progress(len(chapters))
    prog.phase1_complete()

    ingested_count = 0

    for ch in chapters:
        chapter_idx = ch["chapter_index"]
        chapter_path = os.path.join(book_dir, f"{chapter_idx:02d}.json")

        # Check if already ingested (resume-safe)
        if os.path.exists(chapter_path):
            print(f"[INGESTION] Chapter {chapter_idx} already exists (skipping)")
            ingested_count += 1
            prog.chapter_ingested(chapter_idx, ch["chapter_title"])
            continue

        try:
            # Extract doctrine
            doctrine = phase2_doctrine(ch, model=model_phase2)

            # Save doctrine
            with open(chapter_path, "w", encoding="utf-8") as f:
                json.dump(doctrine, f, indent=2, ensure_ascii=False)

            ingested_count += 1
            prog.chapter_ingested(chapter_idx, ch["chapter_title"])

        except (LLMError, ValidationError) as e:
            print(f"[ERROR] Chapter {chapter_idx} extraction failed: {e}")
            print(f"        Retrying with enhanced prompt...")
            
            # Retry once with explicit instruction
            try:
                ch_retry = ch.copy()
                ch_retry["chapter_text"] = (
                    "REMINDER: Extract ALL doctrine from this chapter.\n"
                    "MUST include principles, rules, claims, AND warnings.\n"
                    "Do not leave any field empty.\n\n" +
                    ch["chapter_text"]
                )
                doctrine = phase2_doctrine(ch_retry, model=model_phase2)
                
                with open(chapter_path, "w", encoding="utf-8") as f:
                    json.dump(doctrine, f, indent=2, ensure_ascii=False)
                
                ingested_count += 1
                prog.chapter_ingested(chapter_idx, ch["chapter_title"])
                print(f"        Chapter {chapter_idx} succeeded on retry")
                
            except Exception as e2:
                print(f"        Retry also failed: {e2}")
                print(f"        Skipping chapter {chapter_idx} (resumable)")
                # Continue to next chapter (resumable)
                continue

    # ============ COMPLETE ============
    prog.complete()

    return {
        "book_id": book_id,
        "structure_path": structure_path,
        "chapters_ingested": ingested_count,
        "output_dir": book_dir,
    }
