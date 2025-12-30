from .progress_core import record_progress, load_progress_hashes


def print_progress_summary(book_id: str) -> None:
    seen = load_progress_hashes(book_id)
    print(f"Book {book_id}: {len(seen)} chunks recorded")
