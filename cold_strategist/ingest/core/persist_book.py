"""Persist book artifacts for ingest_v2.

Writes a single YAML file per book under `data/ingest_v2/books/{book_id}.yaml`.
If a YAML already exists for the `book_id`, this function raises an error
to enforce the one-book → one-YAML rule.
"""
import os
import json
from pathlib import Path


BASE = Path("data") / "ingest_v2" / "books"


def _ensure_dir():
    BASE.mkdir(parents=True, exist_ok=True)


def _yaml_dump_safe(obj) -> str:
    try:
        import yaml

        return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    except Exception:
        # Fallback to JSON-looking YAML
        return json.dumps(obj, ensure_ascii=False, indent=2)


def persist(book_id: str, artifacts: dict, overwrite: bool = False):
    _ensure_dir()
    out_path = BASE / f"{book_id}.yaml"
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"Book YAML already exists: {out_path}")
    content = _yaml_dump_safe(artifacts)
    out_path.write_text(content, encoding="utf-8")
    return str(out_path)

