#!/usr/bin/env python3
"""CLI entry point for ingest_v2.

Usage:
    python -m cold_strategist.ingest_v2.cli --pdf path/to/book.pdf --book-id my_book
    python -m cold_strategist.ingest_v2.cli --pdf path/to/book.pdf --book-id my_book --title "My Book Title"
"""
import argparse
import sys
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cold_strategist.ingest_v2.ingest_v2 import ingest_book


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a book using the v2 ingestion pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m cold_strategist.ingest_v2.cli --pdf books/my_book.pdf --book-id my_book

  # With title and authors
  python -m cold_strategist.ingest_v2.cli \\
    --pdf books/my_book.pdf \\
    --book-id my_book \\
    --title "The Art of War" \\
    --authors "Sun Tzu"
        """
    )
    
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to PDF file (or .txt file)"
    )
    
    parser.add_argument(
        "--book-id",
        required=True,
        help="Unique book identifier (used for output filename)"
    )
    
    parser.add_argument(
        "--title",
        help="Book title (if not provided, extracted from filename)"
    )
    
    parser.add_argument(
        "--authors",
        nargs="+",
        help="List of author names"
    )
    
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM for domain classification and memory extraction (default: deterministic)"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing ingestion data and start fresh"
    )
    
    args = parser.parse_args()
    
    try:
        result = ingest_book(
            pdf_path=args.pdf,
            book_id=args.book_id,
            title=args.title,
            authors=args.authors,
            overwrite=args.overwrite
        )
        
        print("\n" + "="*70)
        print("INGESTION SUCCESSFUL")
        print("="*70)
        print(f"Book ID: {result['book_id']}")
        print(f"Title: {result['title']}")
        print(f"Chapters: {result['chapters_count']}")
        print(f"Output: {result['output_path']}")
        print("="*70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nERROR: File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nERROR: Ingestion failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

