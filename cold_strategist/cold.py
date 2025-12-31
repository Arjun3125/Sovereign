#!/usr/bin/env python3
"""
Cold Strategist - Sovereign Counsel Engine

Entry point for normal and war mode analysis.

Usage:
    python cold.py normal --domain career --stakes high
    python cold.py war --domain negotiation --stakes medium --arena career
"""

import sys

from cli.main import main as cli_main


def _run_ingest_books(args):
    # minimal CLI for `cold ingest books [--mode full|fast] [--dry-run]`
    mode = "full"
    dry_run = False
    if "--mode" in args:
        try:
            i = args.index("--mode")
            mode = args[i + 1]
        except Exception:
            pass
    if "--dry-run" in args:
        dry_run = True

    try:
        from knowledge.ingest.ingest_books import ingest as ingest_books
        from knowledge.ingest.build_shelves import build_shelves
    except Exception as e:
        print(f"Ingest modules not available: {e}")
        sys.exit(1)

    # run ingest (reads knowledge/books/raw)
    if dry_run:
        print("Running ingest books in dry-run mode")
    ingest_books()

    # build per-minister shelves/indexes
    build_shelves()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "ingest" and sys.argv[2] == "books":
        _run_ingest_books(sys.argv[3:])
    else:
        cli_main()
