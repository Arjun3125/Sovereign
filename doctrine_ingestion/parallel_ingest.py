from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict

from .chapter_processor import process_chapter
from .assembler import assemble
from .validator import validate
from .storage import store_chapter
from .recovery import should_skip
from .progress import ProgressTracker


def ingest_chapter_job(chapter):
    """Worker job: process a single chapter end-to-end (no side-effects).

    Returns a tuple (chapter.index, chapter, doctrine)
    """
    partials = process_chapter(chapter)
    doctrine = assemble(chapter, partials)
    validate(doctrine)
    return chapter.index, chapter, doctrine


def parallel_ingest(chapters: List, max_workers: int = 4) -> List[int]:
    """Process chapters in parallel while committing to storage in order.

    - Chapters are processed in parallel (one chapter per job)
    - Writes to storage occur in chapter index order (sequential commit)
    - Failures are fail-fast per chapter (they raise from the worker)

    Returns the list of ingested chapter indices (sorted)
    """
    results: Dict[int, Dict] = {}
    submitted = {}

    # Map chapter index to chapter object for ordering info
    chapter_map = {c.index: c for c in chapters}
    indices = sorted(chapter_map.keys())
    if not indices:
        return []

    next_expected = indices[0]

    tracker = ProgressTracker(total=len(chapters))

    # Filter out already-committed chapters before submitting work
    pending = []
    for ch in chapters:
        try:
            if should_skip(ch.book_id, ch):
                tracker.mark_done(ch.index)
                print(f"[SKIPPED] Chapter {ch.index} already committed")
                continue
        except Exception:
            # Propagate errors such as hash mismatch
            raise
        pending.append(ch)

    if not pending:
        print("[ALL CHAPTERS ALREADY INGESTED]")
        return []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for c in pending:
            # Main process owns progress state; mark start before submitting job
            tracker.mark_start(c.index)
            fut = executor.submit(ingest_chapter_job, c)
            submitted[fut] = c.index

        # As futures complete, buffer results and commit in order
        for fut in as_completed(submitted):
            idx, chapter, doctrine = fut.result()
            results[idx] = (chapter, doctrine)

            # Commit any ready, ordered results
            while next_expected in results:
                ch, doc = results.pop(next_expected)
                store_chapter(ch.book_id, ch.index, ch.text, doc)
                # Mark done at commit time (main process owns completion state)
                tracker.mark_done(ch.index)
                next_expected += 1

    # return sorted list of indices that were ingested
    return sorted([i for i in indices if i < next_expected])
