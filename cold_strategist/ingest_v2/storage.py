"""
Storage utilities for ingestion v2.

Handles the MVP folder structure:
- raw_text.json (immutable)
- chapters.json (from Phase-1)
- principles/ (individual JSON files per principle)
- embeddings/ (vector store)
- MANIFEST.json (completion seal)
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any


def ensure_book_structure(book_id: str, base_dir: str = "v2_store") -> Path:
    """Create the MVP folder structure for a book."""
    book_dir = Path(base_dir) / book_id
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (book_dir / "principles").mkdir(exist_ok=True)
    (book_dir / "embeddings").mkdir(exist_ok=True)
    
    return book_dir


def save_raw_text(book_dir: Path, raw_text: str):
    """Save raw text as immutable source."""
    raw_path = book_dir / "raw_text.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({"text": raw_text}, f, indent=2, ensure_ascii=False)


def save_chapters(book_dir: Path, chapters: List[Dict]):
    """Save chapters from Phase-1."""
    chapters_path = book_dir / "chapters.json"
    with open(chapters_path, "w", encoding="utf-8") as f:
        json.dump({"chapters": chapters}, f, indent=2, ensure_ascii=False)


def save_principle(book_dir: Path, principle: Dict):
    """Save a single principle as individual JSON file."""
    principle_id = principle.get("id")
    if not principle_id:
        raise ValueError("Principle must have 'id' field")
    
    principle_path = book_dir / "principles" / f"{principle_id}.json"
    with open(principle_path, "w", encoding="utf-8") as f:
        json.dump(principle, f, indent=2, ensure_ascii=False)


def save_manifest(book_dir: Path, manifest: Dict):
    """Save MANIFEST.json marking book as DONE."""
    manifest_path = book_dir / "MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def load_manifest(book_dir: Path) -> Dict:
    """Load MANIFEST.json if it exists."""
    manifest_path = book_dir / "MANIFEST.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def is_book_sealed(book_dir: Path) -> bool:
    """Check if book is sealed (MANIFEST exists with status DONE)."""
    manifest = load_manifest(book_dir)
    return manifest is not None and manifest.get("status") == "DONE"

