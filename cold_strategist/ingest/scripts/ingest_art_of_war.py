#!/usr/bin/env python3
"""Ingest The Art of War using the new two-phase compiler."""
from cold_strategist.ingest.core import ingest_v2 as ingest_book

result = ingest_book(
    pdf_path="books/The_Art_Of_War.pdf",
    book_id="art_of_war",
    title="The Art of War",
    authors=["Sun Tzu"],
    overwrite=True  # Delete existing data and start fresh
)

print("\n" + "="*70)
print("INGESTION COMPLETE")
print("="*70)
print(f"Book ID: {result['book_id']}")
print(f"Title: {result['title']}")
print(f"Chapters: {result['chapters_count']}")
print(f"Output: {result['output_path']}")
print("="*70)

