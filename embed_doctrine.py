# embed_doctrine.py
# PRODUCTION-SAFE | CLI-ONLY | OLLAMA EMBEDDINGS via Python library

import json
import sqlite3
from pathlib import Path
from ollama import embeddings as ollama_embed

# ---------------- CONFIG ----------------

BOOK = "The_Art_Of_War"
DOCTRINE_FILE = f"workspace/{BOOK}/02_principles.json"
DB_PATH = f"workspace/{BOOK}/embeddings/doctrine_vectors.db"
MODEL = "nomic-embed-text"

# ---------------- EMBED FUNCTION ----------------

def embed(text: str) -> list:
    """
    Call Ollama embedding model via Python library.
    Returns embedding vector as list[float].
    """
    response = ollama_embed(model=MODEL, prompt=text)
    return response["embedding"]

# ---------------- SETUP ----------------

# Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

with open(DOCTRINE_FILE, "r", encoding="utf-8") as f:
    doc_data = json.load(f)

# Extract all claims from all chapters
all_doctrines = []
chapters = doc_data.get("chapters", [])
for ch in chapters:
    ch_index = ch.get("chapter_index", 0)
    ch_title = ch.get("chapter_title", f"Chapter {ch_index}")
    claims = ch.get("claims", [])
    for i, c in enumerate(claims):
        claim_text = c if isinstance(c, str) else c.get("claim", "")
        if claim_text:
            all_doctrines.append({
                "doctrine_id": f"{BOOK}_ch{ch_index}_claim{i}",
                "chapter": ch_title,
                "chapter_index": ch_index,
                "claim": claim_text,
                "book": BOOK,
                "confidence": 0.8,
                "tags": ch.get("domains", ["strategy"]),
                "immutable": True,
            })

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS embeddings (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    embedding TEXT NOT NULL,
    metadata TEXT NOT NULL
)
""")

# ---------------- EMBEDDING LOOP ----------------

inserted = 0
skipped = 0

for d in all_doctrines:
    doctrine_id = d["doctrine_id"]
    text = d["claim"]

    cur.execute("SELECT 1 FROM embeddings WHERE id=?", (doctrine_id,))
    if cur.fetchone():
        skipped += 1
        continue

    vector = embed(text)

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

print(f"✅ Embedding complete")
print(f"Inserted: {inserted}")
print(f"Skipped (already embedded): {skipped}")
