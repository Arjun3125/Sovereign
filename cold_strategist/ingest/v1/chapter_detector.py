import re

CHAPTER_REGEX = re.compile(
    r'^(chapter\s+\d+|chapter\s+[ivxlcdm]+|\d+\.\s+.+)',
    re.IGNORECASE
)


def detect_chapters(pages):
    markers = []

    for page_num, text in pages:
        for line in text.splitlines():
            if CHAPTER_REGEX.match(line.strip()):
                markers.append((page_num, line.strip()))
                break

    if not markers:
        raise RuntimeError("No chapters detected")

    chapters = []
    for i, (start_page, title) in enumerate(markers):
        end_page = (
            markers[i + 1][0] - 1
            if i + 1 < len(markers)
            else pages[-1][0]
        )
        chapters.append((i + 1, title, start_page, end_page))

    return chapters
