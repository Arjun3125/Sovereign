import re
from pathlib import Path

CHAPTER_REGEX = re.compile(r"(chapter\s+\d+[:.\-\s]+.*)", re.IGNORECASE)


def chunk_by_structure(text: str):
    matches = list(CHAPTER_REGEX.finditer(text))
    chunks = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunks.append({
            "title": match.group(1).strip(),
            "content": text[start:end].strip(),
        })

    if not chunks:
        chunks.append({"title": "FULL_TEXT", "content": text})

    return chunks


def run(in_path: Path, out_dir: Path):
    text = in_path.read_text(encoding="utf-8")
    chunks = chunk_by_structure(text)

    out_dir.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(chunks):
        (out_dir / f"section_{i:03}.txt").write_text(f"{c['title']}\n\n{c['content']}", encoding="utf-8")
