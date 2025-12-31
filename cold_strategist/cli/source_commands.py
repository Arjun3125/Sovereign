"""
CLI integration for knowledge source inspection.

Adds flags: --why, --show-source, --open-book to verdict and debate commands.
"""

import sys
from pathlib import Path
from cli.source_inspector import SourceInspector


def add_source_inspection_args(parser):
    """
    Add source inspection arguments to argparse parser.
    
    Usage:
      python -m cli debate --why <chunk_id>
      python -m cli debate --show-source <chunk_id>
      python -m cli debate --open-book <book_id>
    """
    parser.add_argument(
        "--why",
        metavar="CHUNK_ID",
        help="Explain why a chunk was retrieved"
    )
    parser.add_argument(
        "--show-source",
        metavar="CHUNK_ID",
        help="Display full chunk with metadata"
    )
    parser.add_argument(
        "--open-book",
        metavar="BOOK_ID",
        help="Show book metadata and chapters"
    )
    parser.add_argument(
        "--summarize-retrieval",
        action="store_true",
        help="Print retrieval summary (support/counter/neutral)"
    )


def handle_source_inspection(args, retrieval_result):
    """
    Process source inspection flags if present.
    
    Args:
        args: argparse Namespace with flags
        retrieval_result: Result from MinisterRetriever.retrieve_with_traceability()
    
    Returns:
        True if inspection was handled (exit after), False to continue
    """
    inspector = SourceInspector(retrieval_result)
    
    if args.why:
        print(inspector.why(args.why))
        return True
    
    if args.show_source:
        print(inspector.show_source(args.show_source))
        return True
    
    if args.open_book:
        print(inspector.open_book(args.open_book))
        return True
    
    if args.summarize_retrieval:
        print(inspector.summarize())
        return True
    
    return False
