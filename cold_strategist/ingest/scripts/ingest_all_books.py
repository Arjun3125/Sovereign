#!/usr/bin/env python
"""
Ingestion v2: Batch ingestion for all books in workspace.

Processes each book directory in cold_strategist/workspace, extracting 
doctrine through Phase-1 (structuring) and Phase-2 (doctrine extraction).
Resume-safe and progress-tracked.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict

# Add parent directories to path for imports
BASE_DIR = Path(__file__).resolve().parents[3]  # up to repo root
sys.path.insert(0, str(BASE_DIR))

from cold_strategist.ingest.core.ingest_v2 import ingest_v2
from cold_strategist.ingest.core.llm_client import LLMError
from cold_strategist.ingest.core.validators import ValidationError


WORKSPACE_DIR = BASE_DIR / "cold_strategist" / "workspace"
OUTPUT_DIR = BASE_DIR / "v2_store"


def get_book_text(book_dir: Path) -> str:
    """Extract book text from workspace directory.
    
    Looks for:
    1. 00_raw_text.txt (canonical raw text)
    2. raw_text.json (fallback)
    """
    raw_text_path = book_dir / "00_raw_text.txt"
    if raw_text_path.exists():
        with open(raw_text_path, "r", encoding="utf-8") as f:
            return f.read()
    
    # Fallback: check for raw_text.json
    raw_json_path = book_dir / "raw_text.json"
    if raw_json_path.exists():
        with open(raw_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "text" in data:
                return data["text"]
            elif isinstance(data, str):
                return data
    
    raise FileNotFoundError(f"No raw text found in {book_dir}")


def get_book_id(book_dir: Path) -> str:
    """Generate book ID from directory name."""
    return book_dir.name.lower().replace(" ", "_").replace("-", "_")


def ingest_book(book_dir: Path) -> Dict:
    """Ingest a single book through v2 pipeline.
    
    Returns:
        {
            "book_name": str,
            "book_id": str,
            "status": "success" | "skipped" | "error",
            "message": str,
            "result": dict (if success)
        }
    """
    book_name = book_dir.name
    book_id = get_book_id(book_dir)
    
    print(f"\n{'='*70}")
    print(f"INGESTING: {book_name}")
    print(f"{'='*70}")
    
    try:
        # Check if already ingested
        output_book_dir = OUTPUT_DIR / book_id
        if output_book_dir.exists():
            # Check if Phase-2 is complete (all chapters exist)
            chapters_dir = output_book_dir / "chapters"
            if chapters_dir.exists():
                chapter_files = list(chapters_dir.glob("*.json"))
                if len(chapter_files) > 0:
                    print(f"✓ SKIPPED: {book_name} already ingested ({len(chapter_files)} chapters)")
                    return {
                        "book_name": book_name,
                        "book_id": book_id,
                        "status": "skipped",
                        "message": f"Already ingested with {len(chapter_files)} chapters"
                    }
        
        # Load book text
        print(f"→ Loading text from {book_name}...")
        book_text = get_book_text(book_dir)
        print(f"  Text size: {len(book_text)} characters")
        
        # Ingest through v2 pipeline
        print(f"→ Running Phase-1 & Phase-2 ingestion...")
        result = ingest_v2(
            book_text,
            book_id,
            output_dir=str(OUTPUT_DIR)
        )
        
        print(f"✓ SUCCESS: {book_name}")
        print(f"  Chapters: {result.get('chapters_ingested', '?')}")
        print(f"  Output: {result.get('output_dir', '?')}")
        
        return {
            "book_name": book_name,
            "book_id": book_id,
            "status": "success",
            "message": f"Ingested {result.get('chapters_ingested', 0)} chapters",
            "result": result
        }
        
    except (LLMError, ValidationError) as e:
        print(f"✗ ERROR: {book_name} - {e}")
        return {
            "book_name": book_name,
            "book_id": book_id,
            "status": "error",
            "message": str(e)
        }
    except Exception as e:
        print(f"✗ ERROR: {book_name} - {type(e).__name__}: {e}")
        return {
            "book_name": book_name,
            "book_id": book_id,
            "status": "error",
            "message": f"{type(e).__name__}: {e}"
        }


def ingest_all_books() -> Dict:
    """Ingest all books in workspace directory."""
    
    print("\n" + "="*70)
    print("INGESTION V2: BATCH INGESTION")
    print("="*70)
    print(f"Workspace: {WORKSPACE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    # Find all book directories
    book_dirs = sorted([d for d in WORKSPACE_DIR.iterdir() if d.is_dir()])
    
    if not book_dirs:
        print(f"ERROR: No book directories found in {WORKSPACE_DIR}")
        return {"status": "error", "message": "No books found"}
    
    print(f"Found {len(book_dirs)} book(s):")
    for bd in book_dirs:
        print(f"  • {bd.name}")
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ingest each book
    results = []
    for book_dir in book_dirs:
        result = ingest_book(book_dir)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("BATCH INGESTION COMPLETE")
    print("="*70)
    print()
    
    success = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")
    
    print(f"Results:")
    print(f"  ✓ Success:  {success}")
    print(f"  ⊘ Skipped:  {skipped}")
    print(f"  ✗ Errors:   {errors}")
    print()
    
    # Print error details
    if errors > 0:
        print("Errors:")
        for r in results:
            if r["status"] == "error":
                print(f"  • {r['book_name']}: {r['message']}")
        print()
    
    # Save report
    report_path = BASE_DIR / "ingest_batch_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Report saved to: {report_path}")
    print()
    
    return {
        "status": "complete",
        "summary": {
            "total": len(results),
            "success": success,
            "skipped": skipped,
            "errors": errors
        },
        "results": results
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch ingest all books in workspace")
    parser.add_argument("--output", "-o", type=str, help="Override output directory (default: v2_store)")
    args = parser.parse_args()
    
    if args.output:
        OUTPUT_DIR = Path(args.output)
    
    summary = ingest_all_books()
    sys.exit(0 if summary["status"] == "complete" and summary["summary"]["errors"] == 0 else 1)
