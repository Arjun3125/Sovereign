"""
Doctrine Embedding Audit Script
READ-ONLY — NO STATE MUTATION

Run:
    python doctrine_embedding_audit.py /path/to/vector_db

This script inspects a local SQLite-based embedding table named `embeddings`.
It is read-only and will not modify any files.
"""

import sys
import re
import math
from collections import defaultdict
from typing import List, Dict

# -------------------------
# CONFIG — EDIT ONLY THIS
# -------------------------

VECTOR_DB_TYPE = "sqlite"  # sqlite | chroma | custom
MAX_TEXT_LEN = 500
DUPLICATE_SIM_THRESHOLD = 0.97

# forbidden language patterns
FORBIDDEN_PATTERNS = [
    r"\bi suggest\b",
    r"\btherefore\b",
    r"\bthis implies\b",
    r"\boptimal strategy\b",
    r"\brecommend\b",
    r"\bwe should\b",
]

REQUIRED_METADATA_FIELDS = {
    "doctrine_id",
    "book",
    "chapter",
    "confidence",
    "tags",
    "immutable",
}

# -------------------------
# VECTOR DB ADAPTER
# -------------------------

def load_vectors(db_path: str) -> List[Dict]:
    """
    MUST return list of:
    {
        "id": str,
        "text": str,
        "embedding": List[float],
        "metadata": dict
    }
    """
    if VECTOR_DB_TYPE == "sqlite":
        import sqlite3
        import json

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Try common column set: id, text, embedding, metadata
        try:
            cur.execute("SELECT id, text, embedding, metadata FROM embeddings")
        except Exception as exc:
            raise SystemExit(f"Failed to query embeddings table: {exc}")

        rows = cur.fetchall()

        records = []
        for r in rows:
            rec_id = r[0]
            text = r[1] if r[1] is not None else ""
            try:
                embedding = json.loads(r[2]) if r[2] else []
            except Exception:
                # Some stores save BLOB - skip embedding decode errors but keep record
                embedding = []

            try:
                metadata = json.loads(r[3]) if r[3] else {}
            except Exception:
                metadata = {}

            records.append({
                "id": rec_id,
                "text": text,
                "embedding": embedding,
                "metadata": metadata,
            })
        return records

    raise NotImplementedError("Adapter not implemented")


# -------------------------
# UTILITIES
# -------------------------

def cosine_sim(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# -------------------------
# AUDIT CHECKS
# -------------------------

def audit(records: List[Dict]):
    violations = defaultdict(list)

    # 1️⃣ TEXT LENGTH + STRUCTURE
    for r in records:
        text = (r.get("text") or "")

        if len(text) > MAX_TEXT_LEN:
            violations["OVERLONG_TEXT"].append(r["id"])

        # simple heuristic: many sentences => likely multi-claim
        if text.count('.') > 3 or text.count('\n') > 4:
            violations["MULTI_CLAIM_TEXT"].append(r["id"])

    # 2️⃣ FORBIDDEN LANGUAGE (MINISTER / ANALYSIS LEAK)
    for r in records:
        t = (r.get("text") or "").lower()
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, t):
                violations["RUNTIME_LANGUAGE"].append(r["id"])

    # 3️⃣ METADATA INTEGRITY
    for r in records:
        meta = r.get("metadata") or {}

        missing = REQUIRED_METADATA_FIELDS - set(meta.keys())
        if missing:
            violations["MISSING_METADATA"].append((r["id"], list(missing)))

        if meta.get("immutable") is not True:
            violations["MUTABLE_VECTOR"].append(r["id"])

        # check basic types
        if not isinstance(meta.get("tags"), list):
            violations["BAD_TAGS_TYPE"].append(r["id"])

    # 4️⃣ DUPLICATE SEMANTIC ENTRIES (cheap O(n^2) for small stores)
    n = len(records)
    for i in range(n):
        emb_i = records[i].get("embedding") or []
        for j in range(i + 1, n):
            emb_j = records[j].get("embedding") or []
            if not emb_i or not emb_j:
                continue
            sim = cosine_sim(emb_i, emb_j)
            if sim >= DUPLICATE_SIM_THRESHOLD:
                violations["DUPLICATE_SEMANTIC"].append((records[i]["id"], records[j]["id"], round(sim, 3)))

    return violations


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python doctrine_embedding_audit.py <vector_db_path>")
        sys.exit(1)

    db_path = sys.argv[1]
    try:
        records = load_vectors(db_path)
    except Exception as exc:
        print(f"Failed to load vectors: {exc}")
        sys.exit(2)

    print(f"\n🔍 Auditing {len(records)} embeddings from: {db_path}\n")

    violations = audit(records)

    if not violations:
        print("✅ CLEAN — No violations found.")
        sys.exit(0)

    print("🚨 VIOLATIONS DETECTED:\n")

    for k, v in violations.items():
        print(f"❌ {k}: {len(v)}")
        for item in v[:5]:
            print("   →", item)
        if len(v) > 5:
            print("   ...")

    print("\n⛔ DO NOT CONNECT DARBAR UNTIL FIXED.")
