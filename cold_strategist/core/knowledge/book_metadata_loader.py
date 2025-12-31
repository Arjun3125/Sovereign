"""
Book Metadata Loader

Loads metadata for all books in the knowledge base.
Metadata is stored in YAML files alongside PDFs.

Structure:
books/
  metadata/
    art_of_seduction.yaml
    48_laws_of_power.yaml
    on_war.yaml
    ...
"""

import os
import yaml
from typing import Dict, List


# Default metadata if file not found
DEFAULT_METADATA = {
    "domains": [],
    "tones": ["neutral"],
    "priority": {
        "war": 0.5,
        "standard": 0.7,
        "quick": 0.2,
    }
}


class BookMetadataLoader:
    """Load and cache book metadata from YAML files."""

    def __init__(self, metadata_dir: str = None):
        """
        Args:
            metadata_dir: Path to books/metadata/ directory.
                         If None, uses default location relative to project root.
        """
        if metadata_dir is None:
            # Default: cold_strategist/books/metadata/
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            metadata_dir = os.path.join(project_root, "books", "metadata")

        self.metadata_dir = metadata_dir
        self._cache = {}

    def load_all(self) -> Dict[str, Dict]:
        """
        Load metadata for all books.
        
        Returns:
            Dict mapping book_id → metadata dict
            
        Example return:
            {
                "art_of_seduction": {
                    "title": "The Art of Seduction",
                    "author": "Robert Greene",
                    "domains": ["power", "psychology"],
                    "tones": ["dark", "strategic"],
                    "modes": ["war", "standard"],
                    "priority": {"war": 1.0, "standard": 0.7, "quick": 0.2}
                },
                ...
            }
        """
        if not os.path.exists(self.metadata_dir):
            return {}

        all_meta = {}

        for filename in os.listdir(self.metadata_dir):
            if not filename.endswith(".yaml"):
                continue

            book_id = filename.replace(".yaml", "")
            metadata = self.load_one(book_id)
            all_meta[book_id] = metadata

        return all_meta

    def load_one(self, book_id: str) -> Dict:
        """
        Load metadata for a single book.
        
        Args:
            book_id: Book identifier (filename without .yaml)
            
        Returns:
            Metadata dict, or DEFAULT_METADATA if file not found
        """
        if book_id in self._cache:
            return self._cache[book_id]

        filepath = os.path.join(self.metadata_dir, f"{book_id}.yaml")

        if not os.path.exists(filepath):
            metadata = DEFAULT_METADATA.copy()
            metadata["book_id"] = book_id
            self._cache[book_id] = metadata
            return metadata

        try:
            with open(filepath, "r") as f:
                metadata = yaml.safe_load(f)

            # Ensure required fields
            metadata["book_id"] = book_id
            if "domains" not in metadata:
                metadata["domains"] = []
            if "tones" not in metadata:
                metadata["tones"] = []
            if "priority" not in metadata:
                metadata["priority"] = DEFAULT_METADATA["priority"]

            self._cache[book_id] = metadata
            return metadata

        except Exception as e:
            # Fallback to default if parse fails
            print(f"Warning: Failed to load {filepath}: {e}")
            metadata = DEFAULT_METADATA.copy()
            metadata["book_id"] = book_id
            self._cache[book_id] = metadata
            return metadata

    def refresh(self):
        """Clear cache and reload from disk."""
        self._cache.clear()
