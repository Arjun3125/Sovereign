"""
Doctrine Loader
Loads locked, immutable doctrine files.
"""

import yaml
from pathlib import Path


class DoctrineLoader:
    """Loads immutable doctrine files from locked directory."""

    def __init__(self):
        """Initialize the doctrine loader."""
        self.doctrine_dir = Path(__file__).parent / "locked"

    def load_doctrine(self, doctrine_name: str) -> dict:
        """Load a specific doctrine file.
        
        Args:
            doctrine_name: Name of the doctrine to load (without .yaml)
            
        Returns:
            The loaded doctrine as a dictionary
        """
        doctrine_path = self.doctrine_dir / f"{doctrine_name}.yaml"
        if not doctrine_path.exists():
            return {}
        
        with open(doctrine_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def load_all_doctrines(self) -> dict:
        """Load all doctrine files.
        
        Returns:
            Dictionary mapping doctrine names to their content
        """
        doctrines = {}
        for doctrine_file in self.doctrine_dir.glob("*.yaml"):
            name = doctrine_file.stem
            doctrines[name] = self.load_doctrine(name)
        return doctrines
