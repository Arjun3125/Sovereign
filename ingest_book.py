"""
Extract PDF text and run ingestion_v2 pipeline.

Usage:
    python ingest_book.py --pdf "path/to/book.pdf" --book-id "book_id"
"""

import sys
import argparse
import os

# Try different PDF libraries
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ingestion_v2.ingest_v2 import ingest_v2


def extract_pdf_text(pdf_path: str) -> str:
    """
    Extract text from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text

    Raises:
        ImportError: If no PDF library available
        FileNotFoundError: If PDF not found
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Try pdfplumber first (more reliable)
    if pdfplumber is not None:
        print(f"[PDF] Using pdfplumber to extract text...")
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"  Extracting page {page_num}/{len(pdf.pages)}...", end="\r")
                text += page.extract_text() + "\n"
            print(f"  Extracted {len(pdf.pages)} pages                    ")
            return text

    # Fall back to pypdf
    elif pypdf is not None:
        print(f"[PDF] Using pypdf to extract text...")
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages, 1):
            print(f"  Extracting page {page_num}/{len(reader.pages)}...", end="\r")
            text += page.extract_text() + "\n"
        print(f"  Extracted {len(reader.pages)} pages                    ")
        return text

    else:
        raise ImportError(
            "No PDF library available. Install: pip install pdfplumber pypdf"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Extract PDF and ingest using v2 pipeline"
    )
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to PDF file",
    )
    parser.add_argument(
        "--book-id",
        required=True,
        help="Unique book identifier",
    )
    parser.add_argument(
        "--output-dir",
        default="v2_store",
        help="Output directory (default: v2_store)",
    )
    parser.add_argument(
        "--model-phase1",
        help="Phase-1 LLM model (default: env OLLAMA_MODEL)",
    )
    parser.add_argument(
        "--model-phase2",
        help="Phase-2 LLM model (default: env OLLAMA_MODEL)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("INGESTION V2: PDF → DOCTRINE COMPILER")
    print("=" * 70)
    print()

    # Extract PDF
    print(f"[INPUT] PDF: {args.pdf}")
    print(f"[INPUT] Book ID: {args.book_id}")
    print()

    try:
        print("[PHASE 0] Extracting text from PDF...")
        book_text = extract_pdf_text(args.pdf)
        print(f"[PHASE 0] Extracted {len(book_text)} characters")
        print()

        # Run ingestion
        result = ingest_v2(
            book_text=book_text,
            book_id=args.book_id,
            output_dir=args.output_dir,
            model_phase1=args.model_phase1,
            model_phase2=args.model_phase2,
        )

        print()
        print("=" * 70)
        print("INGESTION COMPLETE")
        print("=" * 70)
        print()
        print(f"Book ID:              {result['book_id']}")
        print(f"Structure:            {result['structure_path']}")
        print(f"Chapters Ingested:    {result['chapters_ingested']}")
        print(f"Output Directory:     {result['output_dir']}")
        print()

    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
