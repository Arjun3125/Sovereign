from pathlib import Path
import yaml

from core.knowledge.ingest.extract_pdf import extract_pdf_text
from core.knowledge.ingest.structural_chunker import split_by_structure
from core.knowledge.ingest.semantic_slicer import semantic_slice
from core.knowledge.ingest.indexer import index_chunks as do_index
from rag.index import VectorIndex

# -------------------------
# CONFIG
# -------------------------

BOOKS_ROOT = Path("rag/books")
DEFAULT_MAX_CHUNK_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 200


# -------------------------
# EMBEDDING + INDEXING
# -------------------------

def simple_embed(text: str):
    """
    Placeholder embedding function (token-level char stats).
    Replace with real embeddings (OpenAI, Ollama, etc.) in production.
    """
    if not text or len(text) == 0:
        return [0.0, 0.0, 0.0]
    
    # Use character codes normalized to [0, 1] range
    chars = text[:256]
    mean_ord = sum(ord(c) for c in chars) / len(chars) / 256.0
    std_ord = (sum((ord(c) / 256.0 - mean_ord) ** 2 for c in chars) / len(chars)) ** 0.5
    
    return [
        mean_ord,
        std_ord,
        len(text) % 256 / 256.0
    ]


# Global vector index (persist across book ingestions)
global_index = VectorIndex(simple_embed)


# -------------------------
# LLM CALL WRAPPER (GUARDED)
# -------------------------

def llm_call(prompt: str) -> str:
    """
    Guarded LLM call.
    Must return ONLY split points in strict format.
    """
    # Replace with your actual LLM client
    # Example: return llm.generate(prompt)
    raise NotImplementedError("Connect your LLM client here.")


# -------------------------
# INGESTION PIPELINE
# -------------------------

def ingest_book(book_dir: Path):
    print(f"\n[INGEST] {book_dir.name}")

    meta_path = book_dir / "meta.yaml"
    pdf_path = book_dir / "source.pdf"
    extracted_txt = book_dir / "extracted.txt"

    if not meta_path.exists():
        raise FileNotFoundError(f"Missing meta.yaml in {book_dir}")
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing source.pdf in {book_dir}")

    meta = yaml.safe_load(meta_path.read_text())

    # 1) Extract PDF → raw text (verbatim)
    raw_text = extract_pdf_text(pdf_path, extracted_txt)
    print(f"  - Extracted text length: {len(raw_text)}")

    # 2) Structural chunking (chapters/sections)
    chapter_titles = [c["title"] for c in meta.get("chapters", [])]
    sections = split_by_structure(raw_text, chapter_titles)
    print(f"  - Structural sections: {len(sections)}")

    all_semantic_chunks = []

    # 3) Semantic slicing (LLM-assisted, guarded)
    for sec in sections:
        sec_text = sec["raw_text"]
        if not sec_text.strip():
            continue

        slices = semantic_slice(
            section_text=sec_text,
            llm_call=llm_call,
            max_chunk_chars=DEFAULT_MAX_CHUNK_CHARS,
            overlap_chars=DEFAULT_OVERLAP_CHARS,
        )

        # Attach lineage + authority metadata
        for s in slices:
            s.update({
                "book_id": meta["book_id"],
                "chapter_title": sec["chapter_title"],
                "domains": meta.get("domains", []),
                "allowed_ministers": meta.get("default_ministers", []),
            })

        all_semantic_chunks.extend(slices)

    print(f"  - Semantic chunks: {len(all_semantic_chunks)}")

    # 4) Persist chunks for audit (optional but recommended)
    chunks_dir = book_dir / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    out_path = chunks_dir / "chunks.yaml"
    out_path.write_text(yaml.safe_dump(all_semantic_chunks, sort_keys=False))
    print(f"  - Saved chunks → {out_path}")

    # 5) Index (hook)
    index_chunks(all_semantic_chunks)
    print("  - Indexed")


def index_chunks(chunks):
    """
    Wire to actual indexer: embed and add to vector index with payloads.
    """
    do_index(chunks, simple_embed, global_index)


# -------------------------
# CLI ENTRY
# -------------------------

def main():
    for book_dir in BOOKS_ROOT.iterdir():
        if book_dir.is_dir():
            ingest_book(book_dir)


if __name__ == "__main__":
    main()
