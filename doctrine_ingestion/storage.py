import os
import json
import tempfile
import shutil

BASE = "doctrine_storage/books"


def _paths(book_id, chapter_index):
    book = os.path.join(BASE, book_id)
    raw_dir = os.path.join(book, "raw_chapters")
    doc_dir = os.path.join(book, "doctrine_chapters")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(doc_dir, exist_ok=True)

    raw = os.path.join(raw_dir, f"{chapter_index:02}.txt")
    doc = os.path.join(doc_dir, f"{chapter_index:02}.json")
    return raw, doc


def chapter_exists(book_id, chapter_index):
    _, doc = _paths(book_id, chapter_index)
    return os.path.exists(doc)


def store_chapter(book_id, chapter_index, raw_text, doctrine):
    raw_path, doc_path = _paths(book_id, chapter_index)

    if os.path.exists(doc_path):
        raise RuntimeError("Chapter already committed")

    # --- atomic write via temp files ---
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf_raw:
        tf_raw.write(raw_text)
        raw_tmp = tf_raw.name

    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf_doc:
        json.dump(doctrine, tf_doc, indent=2)
        doc_tmp = tf_doc.name

    shutil.move(raw_tmp, raw_path)
    shutil.move(doc_tmp, doc_path)
