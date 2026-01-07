#!/usr/bin/env python
"""Run ingestion_v2 on the stored raw_text for The Art of War."""
import json
import os
import sys

ROOT = os.getcwd()
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RAW_PATH = os.path.join("cold_strategist", "data", "raw_text", "the_art_of_war.json")

def main():
    if not os.path.exists(RAW_PATH):
        print(f"Raw text not found at {RAW_PATH}; cannot run ingestion.")
        return 2

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("pages", [])
    book_text = "\n".join(p.get("text", "") for p in pages)

    print(f"Loaded {len(pages)} pages; assembling book text ({len(book_text)} chars)")

    try:
        from cold_strategist.ingest_v2.ingest_v2 import ingest_v2
    except Exception as e:
        print(f"Import error: {e}")
        return 3

    try:
        result = ingest_v2(book_text=book_text, book_id="art_of_war", output_dir="v2_store", model_phase1="deepseek-r1-abliterated:8b", model_phase2="deepseek-r1-abliterated:8b")
        print("INGESTION RESULT:")
        print(result)
        return 0
    except Exception as e:
        import traceback
        print(f"Ingestion failed: {e}")
        traceback.print_exc()
        return 4

if __name__ == '__main__':
    sys.exit(main())
