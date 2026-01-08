"""
Post-ingest validation checklist script.

Run this AFTER ingest finishes. It performs the following checks:
1. Ingest completion (metrics file)
2. Duplicate embedding sanity (logs + stores)
3. Vector store integrity (file counts)
4. Resume ledger consistency (ingest_progress.jsonl)
5. Principle schema validation (core knowledge principles + universal)
6. Spot-check retrieval (simple text match fallback)
7. If all pass, create cold_strategist/state/INGEST_LOCK with content 'LOCKED'

This script is read-only until the final step (creating lock).

Do not run automatically; inspect outputs manually before allowing lock creation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional
import datetime

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "cold_strategist" / "state"
METRICS_FILE = STATE_DIR / "ingest_metrics.json"
PROGRESS_FILE = STATE_DIR / "ingest_progress.jsonl"
KNOWLEDGE_DIR = ROOT / "cold_strategist" / "knowledge"
PRINCIPLES_DIR = ROOT / "core" / "knowledge" / "principles"
UNIVERSAL_FILE = KNOWLEDGE_DIR / "universal_principles.jsonl"
LOCK_FILE = STATE_DIR / "INGEST_LOCK"

REQUIRED_PRINCIPLE_KEYS = {"id", "text", "embedding", "book_id", "author"}


def check_completion() -> (bool, str, Dict[str, Any]):
    if not METRICS_FILE.exists():
        return False, "Metrics file missing", {}
    try:
        d = json.loads(METRICS_FILE.read_text())
    except Exception as e:
        return False, f"Failed reading metrics: {e}", {}

    completed = d.get("completed_chunks", 0)
    skipped = d.get("skipped_chunks", 0)
    total = d.get("total_chunks", 0)

    ok = (completed + skipped) == total and total > 0
    reason = "OK" if ok else f"Incomplete: completed+skipped={completed+skipped} total={total}"
    return ok, reason, {"completed": completed, "skipped": skipped, "total": total}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                # Best-effort: skip malformed line but record it
                items.append({"__malformed_line__": line, "__line_no__": i+1})
    return items


def duplicate_embedding_sanity() -> (bool, str, Dict[str, Any]):
    # Look for duplicate principle ids across principles dir and universal file
    issues = []
    id_counts = Counter()

    # Scan principles directory (if exists)
    if PRINCIPLES_DIR.exists():
        for p in PRINCIPLES_DIR.glob("**/*.json"):
            try:
                data = json.loads(p.read_text())
            except Exception:
                continue
            # Accept list or single object
            if isinstance(data, list):
                for item in data:
                    pid = item.get("id") or item.get("principle_id")
                    if pid:
                        id_counts[pid] += 1
            elif isinstance(data, dict):
                pid = data.get("id") or data.get("principle_id")
                if pid:
                    id_counts[pid] += 1

    # Universal principles
    if UNIVERSAL_FILE.exists():
        for item in load_jsonl(UNIVERSAL_FILE):
            pid = item.get("id")
            if pid:
                id_counts[pid] += 1

    # Progress ledger hashes
    seen_hashes = Counter()
    if PROGRESS_FILE.exists():
        for rec in load_jsonl(PROGRESS_FILE):
            h = rec.get("hash") or rec.get("chunk_hash") or rec.get("id")
            if h:
                seen_hashes[h] += 1

    # Issues
    dup_ids = [pid for pid, c in id_counts.items() if c > 1]
    dup_hashes = [h for h, c in seen_hashes.items() if c > 1]

    # Embedding count vs unique principle count
    total_vectors = sum(id_counts.values())
    unique_principles = len(id_counts)

    if dup_ids:
        issues.append(f"Duplicate principle ids found: {len(dup_ids)}")
    if dup_hashes:
        issues.append(f"Duplicate hashes in ledger: {len(dup_hashes)}")
    if total_vectors > unique_principles * 1.05:  # small tolerance
        issues.append(f"Vector count ({total_vectors}) exceeds unique principles ({unique_principles})")

    ok = len(issues) == 0
    reason = "OK" if ok else "; ".join(issues)
    return ok, reason, {"dup_ids": dup_ids[:10], "dup_hashes": dup_hashes[:10], "total_vectors": total_vectors, "unique_principles": unique_principles}


def vector_store_integrity() -> (bool, str, Dict[str, Any]):
    # Heuristic: count files under knowledge directory
    if not KNOWLEDGE_DIR.exists():
        return False, "Knowledge dir missing", {}
    file_count = sum(1 for _ in KNOWLEDGE_DIR.rglob('*') if _.is_file())
    # Simple performance test: ensure not extremely large
    ok = file_count > 0 and file_count < 10_000_000
    reason = "OK" if ok else f"Unexpected file count: {file_count}"
    return ok, reason, {"file_count": file_count}


def ledger_consistency() -> (bool, str, Dict[str, Any]):
    if not PROGRESS_FILE.exists():
        return False, "Progress ledger missing", {}
    seen = set()
    duplicates = []
    malformed = 0
    for rec in load_jsonl(PROGRESS_FILE):
        if "__malformed_line__" in rec:
            malformed += 1
            continue
        bid = rec.get("book_id") or rec.get("source_book") or rec.get("book")
        h = rec.get("hash") or rec.get("chunk_hash") or rec.get("id")
        if not bid or not h:
            # can't validate this line fully
            continue
        key = (bid, h)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    ok = len(duplicates) == 0 and malformed == 0
    reason = "OK" if ok else f"duplicates={len(duplicates)} malformed={malformed}"
    return ok, reason, {"duplicates_sample": duplicates[:5], "malformed": malformed}


def principle_schema_validation() -> (bool, str, Dict[str, Any]):
    missing_examples = []
    total = 0
    checked = 0
    # Check core principles dir
    if PRINCIPLES_DIR.exists():
        for p in PRINCIPLES_DIR.glob("**/*.json"):
            try:
                data = json.loads(p.read_text())
            except Exception:
                continue
            if isinstance(data, list):
                for item in data:
                    total += 1
                    keys = set()
                    keys.add(item.get("id") or item.get("principle_id") or "")
                    # check fields presence
                    present = all((item.get("id") or item.get("principle_id"), item.get("text"), item.get("embedding"), item.get("book_id"), item.get("author")))
                    if not present and len(missing_examples) < 5:
                        missing_examples.append({"file": str(p), "item": item})
            elif isinstance(data, dict):
                total += 1
                present = all((data.get("id") or data.get("principle_id"), data.get("text"), data.get("embedding"), data.get("book_id"), data.get("author")))
                if not present and len(missing_examples) < 5:
                    missing_examples.append({"file": str(p), "item": data})

    # Check universal file
    if UNIVERSAL_FILE.exists():
        for item in load_jsonl(UNIVERSAL_FILE):
            total += 1
            present = all((item.get("id"), item.get("text"), item.get("embedding"), item.get("supporting_books")))
            # universal may not have author/book_id, that's acceptable
            if not present and len(missing_examples) < 5:
                missing_examples.append({"file": str(UNIVERSAL_FILE), "item": item})

    ok = len(missing_examples) == 0 and total > 0
    reason = "OK" if ok else f"missing_examples={len(missing_examples)} total_checked={total}"
    return ok, reason, {"missing_examples": missing_examples, "total_checked": total}


def simple_spot_check_queries(queries: Optional[List[str]] = None) -> Dict[str, Any]:
    # Very small, file-backed search fallback for spot checks
    if queries is None:
        queries = ["What does Sun Tzu say about deception?", "Common patterns in power and timing"]

    # Build small index from universal + core principles texts
    index = []
    def add_from_file(path: Path):
        if not path.exists():
            return
        if path.suffix == ".jsonl":
            for item in load_jsonl(path):
                txt = item.get("text") or item.get("principle") or item.get("principle_text")
                if txt:
                    index.append({"id": item.get("id") or item.get("principle_id"), "text": txt})
        elif path.suffix == ".json":
            try:
                data = json.loads(path.read_text())
            except Exception:
                return
            if isinstance(data, list):
                for it in data:
                    txt = it.get("text") or it.get("principle")
                    if txt:
                        index.append({"id": it.get("id") or it.get("principle_id"), "text": txt})
            elif isinstance(data, dict):
                txt = data.get("text") or data.get("principle")
                if txt:
                    index.append({"id": data.get("id") or data.get("principle_id"), "text": txt})

    # populate
    add_from_file(UNIVERSAL_FILE)
    if PRINCIPLES_DIR.exists():
        for p in PRINCIPLES_DIR.glob("**/*.json"):
            add_from_file(p)

    results = {}
    for q in queries:
        qlower = q.lower()
        matches = [it for it in index if qlower.split()[0] in (it.get("text") or "").lower()]
        # fallback: substring
        if not matches:
            matches = [it for it in index if any(tok in (it.get("text") or "").lower() for tok in qlower.split()[:3])]
        results[q] = {"matches": matches[:5], "count": len(matches)}
    return results


def run_checks(dry_run: bool = True):
    print("Post-ingest validation starting. Dry run:", dry_run)
    checks = []

    ok, reason, meta = check_completion()
    print("1) Ingest completion:", ok, reason, meta)
    checks.append(ok)

    ok2, reason2, meta2 = duplicate_embedding_sanity()
    print("2) Duplicate embedding sanity:", ok2, reason2)
    if meta2:
        print("   meta:", meta2)
    checks.append(ok2)

    ok3, reason3, meta3 = vector_store_integrity()
    print("3) Vector store integrity:", ok3, reason3, meta3)
    checks.append(ok3)

    ok4, reason4, meta4 = ledger_consistency()
    print("4) Resume ledger consistency:", ok4, reason4, meta4)
    checks.append(ok4)

    ok5, reason5, meta5 = principle_schema_validation()
    print("5) Principle schema validation:", ok5, reason5)
    if meta5.get("missing_examples"):
        print("   examples:", meta5.get("missing_examples"))
    checks.append(ok5)

    spot = simple_spot_check_queries()
    print("6) Spot-check retrieval (sample):")
    for q, r in spot.items():
        print(f"   Query: {q}\n     Matches: {r['count']}")

    all_ok = all(checks)
    print("\nSummary: all checks passed?", all_ok)

    if all_ok and not dry_run:
        # create lock file
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.write_text("LOCKED")
        print("Created INGEST_LOCK at", LOCK_FILE)
    elif all_ok and dry_run:
        print("All checks passed. Run with --apply to create INGEST_LOCK.")
    else:
        print("Validation did not pass. Fix issues before freezing ingest.")

    return all_ok


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Post-ingest validation checks and optional lock creation")
    parser.add_argument("--apply", action="store_true", help="If set, create INGEST_LOCK when all checks pass")
    args = parser.parse_args()

    run_checks(dry_run=not args.apply)
