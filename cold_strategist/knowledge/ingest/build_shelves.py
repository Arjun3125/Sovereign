from pathlib import Path
import yaml
import json
from core.rag.vector_store import VectorStore
from core.rag.ingest_principles import extract_principles, write_principles_for_book

SHELVES = Path("knowledge/shelves")
SEMANTIC = Path("knowledge/books/semantic")
INDEX = Path("knowledge/index")
PRINCIPLES_DIR = Path("books/principles")


def build_shelves():
    INDEX.mkdir(parents=True, exist_ok=True)
    PRINCIPLES_DIR.mkdir(parents=True, exist_ok=True)

    for shelf_file in sorted(SHELVES.glob("*.yaml")):
        cfg = yaml.safe_load(shelf_file.read_text(encoding="utf-8")) or {}
        minister = cfg.get("minister") or shelf_file.stem
        books = cfg.get("allowed_books", [])

        store_dir = INDEX / f"{minister.lower()}.index"
        store = VectorStore(path=store_dir)

        all_principles_for_books = {}

        for book in books:
            book_dir = SEMANTIC / book
            principles_accum = []
            if book_dir.exists() and book_dir.is_dir():
                for chunk in sorted(book_dir.glob("*.txt")):
                    chapter_text = chunk.read_text(encoding='utf-8')
                    # use deterministic extractor to produce principle dicts
                    try:
                        principles = extract_principles(chapter_text, {"title": book, "sample_chapter": chunk.stem})
                    except Exception:
                        principles = []

                    for p in principles:
                        # ensure minimal fields
                        text = p.get("text") or p.get("principle") or ""
                        meta = {
                            "book": book,
                            "chapter": p.get("source", {}).get("chapter") or p.get("chapter") or chunk.stem,
                            "source": p.get("source", {}).get("page_range") or chunk.name,
                            "principle_id": p.get("id") or p.get("principle_id") or None,
                        }
                        store.add(text=text, metadata=meta)
                        principles_accum.append(p)

            # persist per-book principles YAML
            if principles_accum:
                try:
                    write_principles_for_book(book, principles_accum, principles_dir=str(PRINCIPLES_DIR))
                except Exception:
                    pass
            all_principles_for_books[book] = principles_accum

        # finalize index
        store.build()
        try:
            store.persist(store_dir)
            print(f"Built shelf for {minister} -> {store_dir}")
        except Exception as e:
            print(f"Failed to persist shelf for {minister}: {e}")


if __name__ == "__main__":
    build_shelves()
