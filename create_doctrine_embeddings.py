#!/usr/bin/env python3
"""
Create doctrine embeddings using Ollama and write per-book SQLite DBs.

Usage:
    python create_doctrine_embeddings.py --workspace ./workspace

This script:
- Scans workspace subfolders for `02_principles.json` (doctrine)
- For each claim in each chapter, creates a doctrine record and embedding
- Writes to `workspace/<BOOK>/embeddings/doctrine_vectors.db`

The DB schema (SQLite):
  CREATE TABLE embeddings (
    id TEXT PRIMARY KEY,
    text TEXT,
    embedding TEXT, -- JSON array
    metadata TEXT   -- JSON object
  );

This is safe to run when no DB exists. If the DB exists, the script will exit to avoid mutating existing embeddings.
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict

from cold_strategist.core.llm.ollama_client import OllamaClient


def collect_doctrine(workspace_dir: Path):
    books = []
    for child in workspace_dir.iterdir():
        if not child.is_dir():
            continue
        doctrine_file = child / "02_principles.json"
        if doctrine_file.exists():
            books.append((child.name, doctrine_file))
    return books


def ensure_db(path: Path):
    if path.exists():
        raise FileExistsError(f"Embedding DB already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE embeddings (
            id TEXT PRIMARY KEY,
            text TEXT,
            embedding TEXT,
            metadata TEXT
        )
        """
    )
    conn.commit()
    return conn


def insert_record(conn: sqlite3.Connection, rec_id: str, text: str, embedding: Any, metadata: Dict[str, Any]):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO embeddings (id, text, embedding, metadata) VALUES (?, ?, ?, ?)",
        (rec_id, text, json.dumps(embedding, ensure_ascii=False), json.dumps(metadata, ensure_ascii=False)),
    )
    conn.commit()


def make_doctrine_records(book_name: str, doctrine_path: Path):
    data = json.loads(doctrine_path.read_text(encoding="utf-8"))
    chapters = data.get("chapters", [])
    records = []
    for ch in chapters:
        idx = ch.get("chapter_index")
        chapter_code = ch.get("chapter_code") or f"C{idx:03d}"
        # tags: use domains as tags
        tags = ch.get("domains") or []
        # confidence: best-effort; if present on chapter use it, else 0.9
        confidence = ch.get("confidence") or 0.9

        # Embed principles? The constitution asked "claim" only, so focus on claims
        claims = ch.get("claims") or []
        claim_texts = []
        for n, c in enumerate(claims, start=1):
            if isinstance(c, dict) and "claim" in c:
                claim_texts.append((n, c.get("claim")))
            elif isinstance(c, str):
                claim_texts.append((n, c))
        # If no claims, optionally fall back to principles
        if not claim_texts:
            principles = ch.get("principles") or []
            for n, p in enumerate(principles, start=1):
                if isinstance(p, str) and p.strip():
                    claim_texts.append((n, p))

        def extract_text_from_claim(c):
            # robust extraction of claim text from varied structures
            if isinstance(c, str):
                return c
            if isinstance(c, dict):
                # common shape: {"claim": "..."} or {"claim": {"text": "..."}}
                if "claim" in c:
                    v = c["claim"]
                    if isinstance(v, str):
                        return v
                    if isinstance(v, dict):
                        # try common keys
                        for k in ("text", "value", "body"):
                            if k in v and isinstance(v[k], str):
                                return v[k]
                # fallback: search for any string value in dict
                for v in c.values():
                    if isinstance(v, str):
                        return v
            return None

        for n, c in claim_texts:
            text = extract_text_from_claim(c) if not isinstance(c, str) else c
            if not text:
                # if c was a tuple (n, str) previously handled above; ensure string
                if isinstance(c, str):
                    text = c
            if not text or not str(text).strip():
                continue
            doctrine_id = f"{book_name}_{chapter_code}_CL{n:02d}"
            metadata = {
                "doctrine_id": doctrine_id,
                "book": book_name,
                "chapter": chapter_code,
                "confidence": float(confidence),
                "tags": tags,
                "source_ref": f"{chapter_code}",
                "immutable": True,
            }
            records.append((doctrine_id, str(text).strip(), metadata))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    parser.add_argument("--model", default=None, help="Ollama embed model override (optional)")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.exists():
        print(f"Workspace not found: {workspace}")
        return

    books = collect_doctrine(workspace)
    if not books:
        print("No doctrine files (02_principles.json) found in workspace subfolders.")
        return

    client = OllamaClient()

    for book_name, doctrine_path in books:
        print(f"Processing book: {book_name} -> {doctrine_path}")
        records = make_doctrine_records(book_name, doctrine_path)
        if not records:
            print(f"  No claim records found for {book_name}; skipping.")
            continue

        db_path = workspace / book_name / "embeddings" / "doctrine_vectors.db"
        if db_path.exists():
            print(f"  Embedding DB already exists: {db_path} - skipping to avoid mutation")
            continue

        try:
            conn = ensure_db(db_path)
        except FileExistsError as exc:
            print(f"  {exc}")
            continue

        try:
            for rec_id, text, metadata in records:
                print(f"  Embedding {rec_id} (len={len(text)})")
                emb = client.embed(text)
                insert_record(conn, rec_id, text, emb, metadata)
        finally:
            conn.close()
            print(f"  Wrote embeddings to: {db_path}")

    print("Done.")


if __name__ == "__main__":
    main()
