from typing import List, Dict
import re


def split_by_structure(
    raw_text: str,
    chapter_markers: List[str],
    case_insensitive: bool = True,
) -> List[Dict]:
    """
    Split raw text into structural sections using explicit chapter markers.

    Args:
        raw_text: Full extracted book text
        chapter_markers: Ordered list of chapter/section titles
        case_insensitive: Whether to match markers case-insensitively

    Returns:
        List of dicts with:
          - chapter_title
          - raw_text (section content)
    """
    if not chapter_markers:
        raise ValueError("chapter_markers must be a non-empty list")

    flags = re.IGNORECASE if case_insensitive else 0

    # Build regex that captures chapter titles
    escaped = [re.escape(m) for m in chapter_markers]
    pattern = r"(" + "|".join(escaped) + r")"
    regex = re.compile(pattern, flags)

    matches = list(regex.finditer(raw_text))
    if not matches:
        # Fallback: entire text as one section
        return [{
            "chapter_title": "UNSTRUCTURED",
            "raw_text": raw_text.strip()
        }]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)

        chapter_title = match.group(1)
        section_text = raw_text[start:end].strip()

        sections.append({
            "chapter_title": chapter_title,
            "raw_text": section_text
        })

    return sections


def detect_simple_chapters(raw_text: str) -> List[str]:
    """
    Optional helper to auto-detect simple chapter headers.
    (Use only if metadata not provided.)
    """
    candidates = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if (
            len(line) < 120
            and len(line) > 3
            and line.isupper()
        ):
            candidates.append(line)
    return list(dict.fromkeys(candidates))


if __name__ == "__main__":
    # Simple smoke test
    text = """
    CHAPTER ONE
    This is the beginning.

    CHAPTER TWO
    This is the continuation.
    """
    chapters = ["CHAPTER ONE", "CHAPTER TWO"]
    sections = split_by_structure(text, chapters)
    for s in sections:
        print("===", s["chapter_title"], "===")
        print(s["raw_text"])
