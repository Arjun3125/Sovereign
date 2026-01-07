
from .pdf_reader import extract_pages
from .chapter_detector import detect_chapters
from .chapter_model import Chapter
from .parallel_ingest import parallel_ingest


def ingest_book(pdf_path: str, book_id: str, workers: int = 4):
    pages = extract_pages(pdf_path)
    chapter_defs = detect_chapters(pages)

    chapters = []
    for index, title, start, end in chapter_defs:
        text = "\n".join(p[1] for p in pages if start <= p[0] <= end)
        chapters.append(
            Chapter(
                book_id=book_id,
                index=index,
                title=title,
                text=text,
                start_page=start,
                end_page=end,
                hash=Chapter.compute_hash(text),
            )
        )

    return parallel_ingest(chapters, max_workers=workers)
