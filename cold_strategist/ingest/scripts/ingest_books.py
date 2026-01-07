#!/usr/bin/env python
import sys
import os
import argparse
import glob
import json
from pathlib import Path

# Add parent directories to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT.parent))

# Ingest freeze gate: prevents accidental runs while a lock exists.
# To force, pass --force on the command line.
LOCK_FILE = Path("cold_strategist/state/INGEST_LOCK")
if LOCK_FILE.exists() and "--force" not in sys.argv:
    raise RuntimeError(
        "INGEST LOCKED. Remove cold_strategist/state/INGEST_LOCK or pass --force."
    )

from core.ingest.extract_pdf import extract
from core.ingest.structural_chunker import chunk_structure
from core.ingest.semantic_slicer import semantic_slice
from core.ingest.principle_extractor import extract_principles
from core.ingest.minister_affinity import tag
from core.ingest.persist_chunks import persist
from core.ingest.validate import ValidationError, validate_raw, validate_structural, validate_semantic, validate_principles, validate_affinity
from core.ingest.report import build_report, add_warning
try:
    from core.knowledge.store import ingest_validated
except Exception:
    ingest_validated = None


def _p(*parts) -> str:
    """Return a string path under PROJECT_ROOT."""
    return str(PROJECT_ROOT.joinpath(*parts))


def ingest_folder(folder: str, mode: str, war_shelf: bool, dry_run: bool, overwrite: bool):
    reports = []
    print('>>> ABOUT TO CREATE KNOWLEDGE DIR')
    # Ensure knowledge root and subfolders exist and are deterministic
    knowledge_root = PROJECT_ROOT.joinpath("core", "knowledge")
    knowledge_root.mkdir(parents=True, exist_ok=True)
    (knowledge_root / "principles").mkdir(parents=True, exist_ok=True)
    (knowledge_root / "shelves").mkdir(parents=True, exist_ok=True)
    (knowledge_root / "index").mkdir(parents=True, exist_ok=True)

    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    for pdf in pdfs:
        try:
            raw_text_dir = _p("data", "raw_text")
            Path(raw_text_dir).mkdir(parents=True, exist_ok=True)
            book = extract(pdf, raw_text_dir)
        except Exception as e:
            print(f"Failed to extract {pdf}: {e}")
            print('>>> EXITING EARLY HERE (extract failure)')
            continue

        raw_path = Path(_p("data", "raw_text", f"{book}.json"))
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)

        print(f"Processing {book} -> mode={mode} dry_run={dry_run}")

        # Classical profile detection (tune validator for classical texts)
        book_slug = str(book).replace(" ", "_").lower()
        is_classical = True if "art_of_war" in book_slug else False

        # Structural
        structural = chunk_structure(raw)
        structural_dir = Path(_p("data", "structural"))
        structural_dir.mkdir(parents=True, exist_ok=True)
        with open(structural_dir.joinpath(f"{book}.json"), "w", encoding="utf-8") as f:
            json.dump(structural, f, ensure_ascii=False, indent=2)

        semantic = {}
        principles = {}
        affinity = {}

        if mode == "full":
            # Semantic (LLM-guarded; writes to data/semantic)
            semantic_out = _p("data", "semantic")
            Path(semantic_out).mkdir(parents=True, exist_ok=True)
            semantic = semantic_slice(structural, out_dir=semantic_out, llm_guarded=False)

            # Principles
            principles_out = _p("data", "principles")
            Path(principles_out).mkdir(parents=True, exist_ok=True)
            # TEMPORARY DIAGNOSTIC: force extractor call and print diagnostics
            print(">>> CALLING EXTRACT_PRINCIPLES")
            principles = extract_principles(semantic, out_dir=principles_out, profile=("classical" if is_classical else "default"))
            try:
                count = len(principles.get('principles', principles) if isinstance(principles, dict) else principles)
                print(">>> RETURNED FROM EXTRACT_PRINCIPLES", count)
            except Exception:
                print(">>> RETURNED FROM EXTRACT_PRINCIPLES (could not compute length)")

            # DIAGNOSTIC: persist extracted principles directly into core knowledge store (temporary)
            try:
                extracted = principles.get('principles') if isinstance(principles, dict) else principles
                if not extracted:
                    print('>>> NO PRINCIPLES EXTRACTED')
                else:
                    if ingest_validated is None:
                        print('>>> ingest_validated unavailable; skipping persistence')
                    else:
                        print(f'>>> PERSISTING {len(extracted)} EXTRACTED PRINCIPLES')
                        for i, p in enumerate(extracted):
                            # Build a minimal canonical principle for ingestion
                            text = p.get('principle') or p.get('principle_text') or p.get('text') or ''
                            explanation = p.get('explanation') or ''
                            canonical = {
                                'principle_id': (str(hash(text + str(i)))[:20]),
                                'principle': text,
                                'explanation': explanation,
                                'domain_fit': p.get('domain_fit', []),
                                'applicable_when': p.get('conditions', []),
                                'not_applicable_when': p.get('counter_conditions', []),
                                'confidence_weight': 0.5,
                                'source': {'book': book, 'chapter': p.get('derived_from') or 'extracted'},
                            }
                            try:
                                status = ingest_validated(canonical)
                                print('>>> INGESTED', status.get('principle_id'))
                            except Exception as e:
                                print('>>> INGEST FAILED', e)
            except Exception as e:
                print('>>> ERROR DURING DIAGNOSTIC PERSIST', e)

            # Affinity tagging
            affinity_out = _p("data", "affinity")
            Path(affinity_out).mkdir(parents=True, exist_ok=True)
            affinity = tag(principles, out_dir=affinity_out, war_weight=0.5 if not war_shelf else 0.8)

            # Validation
            try:
                validate_raw(raw)
                validate_structural(structural)
                validate_semantic(semantic)
                validate_principles(principles)
                validate_affinity(affinity)
            except ValidationError as ve:
                report = {"book_id": book, "status": "failed", "error": str(ve)}
                print(f"Validation failed for {book}: {ve}")
                print('>>> EXITING EARLY HERE (validation failure)')
                reports.append(report)
                continue

            # Build report
            report = build_report(book, raw, structural, semantic, principles, affinity)
            reports.append(report)

            # Print report for dry-run visibility (but still persist for mode=full)
            if dry_run:
                print(json.dumps(report, indent=2))

                # Diagnostic: unguarded persistence for debugging
                print("DEBUG: about to persist principles")
                persist(book,
                    _p("data", "structural", f"{book}.json"),
                    _p("data", "semantic", f"{book}.json"),
                    _p("data", "principles", f"{book}.json"),
                    _p("data", "affinity", f"{book}.json"))
                print(f"Wrote rag_store/books/{book}")
        else:
            # Fast mode: only structural written
            report = {"book_id": book, "status": "ok", "notes": "fast mode - only structural"}
            reports.append(report)
            if dry_run:
                print(json.dumps(report, indent=2))

    if dry_run:
        print(json.dumps(reports, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('folder')
    p.add_argument('--mode', choices=['fast', 'full', 'ingest'], default='full')
    p.add_argument('--war-shelf', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args()

    # Bind 'full' and 'ingest' to the ingest pipeline explicitly
    if args.mode in ("ingest", "full"):
        print(">>> CALLING INGEST PIPELINE")
        ingest_folder(args.folder, 'full', args.war_shelf, args.dry_run, args.overwrite)
    else:
        # fallback to existing behavior (fast)
        ingest_folder(args.folder, args.mode, args.war_shelf, args.dry_run, args.overwrite)


if __name__ == '__main__':
    main()
