"""
Cross-Book Synthesis — Core Design

Phases implemented:
- Phase 1: Load principle pool (principle_store.get_all())
- Phase 2: HDBSCAN clustering over embeddings
- Phase 3: Cross-book gate (clusters must span >= 2 books)
- Phase 4: Deterministic LLM-based synthesis (single, cold principle)
- Phase 5: Authority elevation: create universal principle records
- Phase 6: Store as JSONL and provide integration hooks

This module does not execute anything on import; call `build_universal_principles(...)` to run.
"""

from __future__ import annotations

import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Iterable
from collections import defaultdict

try:
    import numpy as np
except Exception:  # pragma: no cover - helpful error for missing deps
    raise ImportError("numpy is required for synthesis; please install numpy")

try:
    import hdbscan
except Exception:  # pragma: no cover
    raise ImportError("hdbscan is required for clustering; please install hdbscan")

from cold_strategist.core.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


REQUIRED_PRINCIPLE_FIELDS = {"principle_id", "text", "embedding", "book_id", "author"}


def validate_principles(principles: Iterable[Dict[str, Any]]):
    """Ensure every principle conforms to canonical data contract."""
    for p in principles:
        missing = REQUIRED_PRINCIPLE_FIELDS - set(p.keys())
        if missing:
            raise ValueError(f"Principle missing required fields: {missing} \nPrinciple: {p}")


def load_principle_pool(principle_store) -> List[Dict[str, Any]]:
    """Phase 1 — canonical pool. Only extracted principles are used.

    The `principle_store` must expose `get_all()` which returns an iterable of
    dicts that satisfy the canonical data contract.
    """
    principles = list(principle_store.get_all())
    validate_principles(principles)
    logger.info("Loaded %d principles from store", len(principles))
    return principles


def cluster_principles(principles: List[Dict[str, Any]], *, min_cluster_size: int = 3, min_samples: int = 2) -> List[int]:
    """Phase 2 — semantic clustering using HDBSCAN on embeddings.

    Returns `labels` aligned with `principles`.
    """
    X = np.array([p["embedding"] for p in principles], dtype=float)
    if X.ndim != 2:
        raise ValueError("Embeddings must be 2D array-like")

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric="euclidean")
    labels = clusterer.fit_predict(X)
    logger.info("HDBSCAN produced %d clusters (label -1 are noise)", len(set(labels)) - (1 if -1 in labels else 0))
    return labels.tolist()


def apply_cross_book_gate(principles: List[Dict[str, Any]], labels: List[int]) -> Dict[int, List[Dict[str, Any]]]:
    """Phase 3 — keep only clusters that cover >= 2 distinct books.

    Returns mapping cid -> member list (members are principle dicts).
    """
    clusters = defaultdict(list)
    for lbl, p in zip(labels, principles):
        if lbl == -1:
            continue
        clusters[lbl].append(p)

    universal = {}
    for cid, members in clusters.items():
        book_ids = {m["book_id"] for m in members}
        if len(book_ids) >= 2:
            universal[cid] = members
        else:
            logger.debug("Cluster %s rejected by cross-book gate (books=%s)", cid, book_ids)

    logger.info("Universal clusters after gate: %d", len(universal))
    return universal


SYNTHESIS_PROMPT_TEMPLATE = """
You are extracting a universal strategic principle from the statements below.
Rules:
- Extract ONE concise principle only.
- Use no author names or references.
- No moralizing language; be cold and operational.
- Produce at most two sentences.
- Principle must survive culture, era, and domain changes.
- Output exactly the principle text only (no bullet, numbering, or explanation).

Statements:
{statements}

Respond with the single principle now:
"""


def synthesize_cluster(cluster: List[Dict[str, Any]], ollama: OllamaClient) -> str:
    """Phase 4 — deterministic synthesis via LLM.

    The function composes statements from cluster members and calls the
    provided `ollama` client to produce a single canonical principle.
    """
    # Compose statements deterministically: sort by book_id then principle_id
    sorted_members = sorted(cluster, key=lambda p: (p["book_id"], p["principle_id"]))
    statements = "\n".join(f"- {m['text']}" for m in sorted_members)
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(statements=statements)

    # Use reason model (deep analysis). OllamaClient.reason() returns text.
    # Determinism: rely on fixed prompt and stable model; ensure no creative framing.
    result = ollama.reason(prompt)
    # Clean result — enforce single principle, strip extraneous whitespace/newlines.
    principle_text = " ".join(line.strip() for line in result.splitlines() if line.strip())
    # Truncate to two sentences if model exceeded the limit
    # Simple sentence split on period — keep at most two sentences.
    sentences = [s.strip() for s in principle_text.split(".") if s.strip()]
    if not sentences:
        raise RuntimeError("LLM returned empty synthesis for cluster")
    principle = ". ".join(sentences[:2])
    # Ensure no trailing period duplication
    if not principle.endswith("."):
        principle = principle
    return principle


def synthesize_universal_principles(principle_store, ollama: OllamaClient, *, min_cluster_size: int = 3, min_samples: int = 2, out_path: Path | str = None) -> List[Dict[str, Any]]:
    """Full pipeline: cluster, gate, synthesize, embed, and write results.

    Returns list of universal principle records.
    """
    principles = load_principle_pool(principle_store)
    labels = cluster_principles(principles, min_cluster_size=min_cluster_size, min_samples=min_samples)
    clusters = apply_cross_book_gate(principles, labels)

    universal_records = []
    for cid, members in clusters.items():
        text = synthesize_cluster(members, ollama)
        supporting_books = sorted({m["book_id"] for m in members})
        supporting_authors = sorted({m["author"] for m in members})
        support_count = len(members)

        # Deterministic id: sha256 of sorted supporting books + text
        id_source = "|".join(supporting_books) + "::" + text
        uid = hashlib.sha256(id_source.encode("utf-8")).hexdigest()[:20]
        record_id = f"universal_{uid}"

        # Compute embedding for universal principle
        embedding = ollama.embed(text)

        record = {
            "id": record_id,
            "text": text,
            "supporting_books": supporting_books,
            "supporting_authors": supporting_authors,
            "support_count": support_count,
            "embedding": embedding,
        }
        universal_records.append(record)
        logger.info("Synthesized universal principle %s (support=%d books=%d)", record_id, support_count, len(supporting_books))

    # Persist results if requested
    if out_path:
        outp = Path(out_path)
        outp.parent.mkdir(parents=True, exist_ok=True)
        with outp.open("w", encoding="utf-8") as fh:
            for r in universal_records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info("Wrote %d universal principles to %s", len(universal_records), outp)

    return universal_records


def query_priority_order():
    """Phase 6 — integration hint: query order.

    Returns an ordered list of keys indicating retrieval preference.
    """
    return ["universal_principles", "book_principles", "raw_excerpts"]


# Lightweight CLI helper (does not run on import)
if __name__ == "__main__":
    import argparse
    from importlib import import_module
    import sys
    # Synthesis freeze gate: same rule as ingest. Do not run if lock exists.
    LOCK_FILE = Path("cold_strategist/state/INGEST_LOCK")
    if LOCK_FILE.exists() and "--force" not in sys.argv:
        raise RuntimeError(
            "INGEST LOCKED. Remove cold_strategist/state/INGEST_LOCK or pass --force."
        )

    parser = argparse.ArgumentParser(description="Build universal principles from principle store")
    parser.add_argument("principle_store_module", help="Module path exposing 'get_principle_store()' returning store object")
    parser.add_argument("--out", help="Output JSONL file path", default="cold_strategist/knowledge/universal_principles.jsonl")
    parser.add_argument("--min_cluster_size", type=int, default=3)
    parser.add_argument("--min_samples", type=int, default=2)

    args = parser.parse_args()

    mod = import_module(args.principle_store_module)
    if not hasattr(mod, "get_principle_store"):
        raise SystemExit("Module must expose get_principle_store()")
    store = mod.get_principle_store()
    ollama = OllamaClient()
    synths = synthesize_universal_principles(store, ollama, min_cluster_size=args.min_cluster_size, min_samples=args.min_samples, out_path=args.out)
    print(f"Wrote {len(synths)} universal principles to {args.out}")
