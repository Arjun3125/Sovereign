import glob
import pathlib
from .extract_pdf import extract
from .structural_chunker import chunk_structure
from .semantic_slicer import semantic_slice
from .principle_extractor import extract_principles
from .minister_affinity import tag
from .persist_chunks import persist


def ingest(folder: str, mode: str = "full") -> None:
    folder = pathlib.Path(folder)
    for pdf in folder.glob("*.pdf"):
        book = extract(str(pdf), "data/raw_text")
        struct_in = f"data/structural/{book}.json"
        # ensure structural output directory
        pathlib.Path("data/structural").mkdir(parents=True, exist_ok=True)
        struct = chunk_structure(__import__('json').load(open(f"data/raw_text/{book}.json", 'r', encoding='utf-8')))
        with open(struct_in, "w", encoding='utf-8') as f:
            import json
            json.dump(struct, f, ensure_ascii=False, indent=2)

        if mode == "full":
            semantic = semantic_slice(struct, out_dir="data/semantic")
            principles = extract_principles(semantic, out_dir="data/principles")
            affin = tag(principles, out_dir="data/affinity")
            persist(book,
                    f"data/structural/{book}.json",
                    f"data/semantic/{book}.json",
                    f"data/principles/{book}.json",
                    f"data/affinity/{book}.json")
