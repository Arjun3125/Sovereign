import json
from .hash_registry import load_registry, save_registry, doctrine_hash
from .domain_vector_manager import DomainVectorStore
from ..models.embedding_client import embed_text
from ..config.domains import DOMAIN_INDEX

def build_embedding_text(d: dict) -> str:
    """Build searchable text from doctrine."""
    return f"""Principle: {d['principle']}
Claim: {d.get('claim','')}
Warning: {d.get('warning','')}
Context: {', '.join(d['domains'])}""".strip()

def run_embedding(doctrine_path="sovereign/data/doctrine_units.json"):
    """Main ingestion: embed doctrines, skip duplicates."""
    with open(doctrine_path) as f:
        doctrines = json.load(f)
    
    registry = load_registry()

    for d in doctrines:
        h = doctrine_hash(d)
        if h in registry:
            continue

        text = build_embedding_text(d)
        vector = embed_text(text)

        for domain in d["domains"]:
            store = DomainVectorStore(DOMAIN_INDEX[domain])
            store.add(vector, {
                "doctrine_id": d["doctrine_id"],
                "confidence": d["confidence"],
                "domain": domain,
                "source": d["source"]
            })
            store.save()

        registry[h] = {
            "doctrine_id": d["doctrine_id"],
            "domains": d["domains"]
        }

    save_registry(registry)
    print(f"Embedded {len(registry)} doctrines")
