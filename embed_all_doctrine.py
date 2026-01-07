# embed_all_doctrine.py
# Generate doctrine embeddings for ALL books in workspace

import json
import sqlite3
import os
from pathlib import Path
from ollama import embeddings as ollama_embed

MODEL = "nomic-embed-text"

def extract_doctrines_from_principles(book_name, principles_file):
    """Extract doctrine claims from 02_principles.json."""
    with open(principles_file, "r", encoding="utf-8") as f:
        doc_data = json.load(f)

    doctrines = []
    chapters = doc_data.get("chapters", [])
    for ch in chapters:
        ch_index = ch.get("chapter_index", 0)
        ch_title = ch.get("chapter_title", f"Chapter {ch_index}")
        claims = ch.get("claims", [])
        for i, c in enumerate(claims):
            claim_text = c if isinstance(c, str) else c.get("claim", "")
            if claim_text:
                doctrines.append({
                    "doctrine_id": f"{book_name}_ch{ch_index}_claim{i}",
                    "chapter": ch_title,
                    "chapter_index": ch_index,
                    "claim": claim_text,
                    "book": book_name,
                    "confidence": 0.8,
                    "tags": ch.get("domains", ["general"]),
                    "immutable": True,
                })
    return doctrines

def embed_text(text):
    """Embed a single text using Ollama."""
    try:
        response = ollama_embed(model=MODEL, prompt=text)
        return response["embedding"]
    except Exception as e:
        print(f"  ⚠️  Embedding failed: {e}")
        return None

def embed_book(book_folder):
    """Embed all doctrines for a single book."""
    principles_file = book_folder / "02_principles.json"
    db_path = book_folder / "embeddings" / "doctrine_vectors.db"

    if not principles_file.exists():
        print(f"❌ {book_folder.name}: no 02_principles.json")
        return 0

    book_name = book_folder.name
    print(f"\n📖 {book_name}:")

    doctrines = extract_doctrines_from_principles(book_name, principles_file)
    if not doctrines:
        print(f"  ❌ No doctrines extracted")
        return 0

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadata TEXT NOT NULL
        )
    """)

    inserted = 0
    skipped = 0

    for d in doctrines:
        doctrine_id = d["doctrine_id"]
        text = d["claim"]

        cur.execute("SELECT 1 FROM embeddings WHERE id=?", (doctrine_id,))
        if cur.fetchone():
            skipped += 1
            continue

        vector = embed_text(text)
        if vector is None:
            continue

        cur.execute(
            "INSERT INTO embeddings VALUES (?,?,?,?)",
            (
                doctrine_id,
                text,
                json.dumps(vector),
                json.dumps(d),
            )
        )
        inserted += 1

    conn.commit()
    conn.close()

    print(f"  ✅ Inserted: {inserted} | Skipped: {skipped}")
    return inserted

# Main
if __name__ == "__main__":
    workspace = Path("workspace")
    total_embedded = 0

    print("=" * 60)
    print("MULTI-BOOK DOCTRINE EMBEDDING")
    print("=" * 60)

    for book_folder in sorted(workspace.iterdir()):
        if book_folder.is_dir():
            n = embed_book(book_folder)
            total_embedded += n

    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: {total_embedded} doctrines embedded")
    print("=" * 60)
