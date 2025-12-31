from pathlib import Path
from knowledge.ingest.extract_pdf import extract_pdf
from knowledge.ingest.structural_chunker import run as structural_run
from knowledge.ingest.semantic_slicer import semantic_slice

RAW = Path("knowledge/books/raw")
EXTRACTED = Path("knowledge/books/extracted")
STRUCTURED = Path("knowledge/books/structured")
SEMANTIC = Path("knowledge/books/semantic")


def ingest():
    for pdf in RAW.glob("*.pdf"):
        try:
            print(f"Ingesting {pdf.name}")

            extracted = EXTRACTED / f"{pdf.stem}.txt"
            ok = extract_pdf(pdf, extracted)
            if not ok:
                print(f"Skipping structural/semantic steps for {pdf.name}")
                continue

            struct_dir = STRUCTURED / pdf.stem
            structural_run(extracted, struct_dir)

            sem_dir = SEMANTIC / pdf.stem
            sem_dir.mkdir(parents=True, exist_ok=True)

            for section in struct_dir.glob("*.txt"):
                sliced = semantic_slice(section.read_text(encoding='utf-8'))
                (sem_dir / section.name).write_text(sliced, encoding="utf-8")
        except Exception as e:
            print(f"Failed ingest for {pdf.name}: {e}")
            continue


if __name__ == "__main__":
    ingest()
