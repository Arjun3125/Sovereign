import argparse
from doctrine_ingestion.ingest import ingest_book


def main():
    p = argparse.ArgumentParser(description="Doctrine Ingestion CLI")
    p.add_argument("--pdf", required=True, help="Path to PDF file")
    p.add_argument("--book-id", required=True, help="Unique book identifier")
    p.add_argument("--workers", type=int, default=4, help="Parallel workers")

    args = p.parse_args()

    ingest_book(
        pdf_path=args.pdf,
        book_id=args.book_id,
        workers=args.workers
    )


if __name__ == "__main__":
    main()
