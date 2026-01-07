import json
import hashlib
from pathlib import Path

REGISTRY_PATH = Path("sovereign/data/embedded_hashes.json")

def load_registry() -> dict:
    """Load hash registry (anti-duplication)."""
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {}

def save_registry(registry: dict):
    """Save hash registry."""
    REGISTRY_PATH.parent.mkdir(exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))

def doctrine_hash(doctrine: dict) -> str:
    """Compute stable hash of doctrine (principle + claim + warning + chapter)."""
    raw = (
        doctrine["principle"]
        + doctrine.get("claim", "")
        + doctrine.get("warning", "")
        + doctrine["source"]["chapter"]
    )
    return hashlib.sha256(raw.encode()).hexdigest()
