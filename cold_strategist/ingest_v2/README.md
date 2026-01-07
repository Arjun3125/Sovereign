# Ingest V2 - New Ingestion Model

A complete ingestion pipeline for processing books and extracting structured knowledge.

## Overview

The ingest_v2 pipeline processes books through the following steps:

1. **Text Extraction**: Reads PDF or text files
2. **Chapter Building**: Splits text into chapters using heuristics
3. **Domain Classification**: Classifies each chapter into domains (deterministic keyword-based)
4. **Memory Extraction**: Extracts memory-grade items for each (chapter, domain) pair
5. **Aggregation**: Combines all data into a structured book artifact
6. **Validation**: Validates the structure against schema
7. **Persistence**: Saves to YAML file in `data/ingest_v2/books/`

## Usage

### Command Line

```bash
# Basic usage
python -m cold_strategist.ingest_v2.cli --pdf path/to/book.pdf --book-id my_book

# With title and authors
python -m cold_strategist.ingest_v2.cli \
  --pdf books/my_book.pdf \
  --book-id my_book \
  --title "The Art of War" \
  --authors "Sun Tzu"
```

### Python API

```python
from cold_strategist.ingest_v2 import ingest_book

result = ingest_book(
    pdf_path="books/my_book.pdf",
    book_id="my_book",
    title="My Book Title",
    authors=["Author Name"]
)

print(f"Saved to: {result['output_path']}")
```

## Output Structure

The pipeline produces a YAML file at `data/ingest_v2/books/{book_id}.yaml` with the following structure:

```yaml
book_id: my_book
title: My Book Title
authors: []
chapters:
  - chapter_id: "1"
    title: "Chapter 1"
    domains:
      - grand_strategy
      - power
    memory:
      - domain: grand_strategy
        memory_items:
          - "Strategic principle 1"
          - "Strategic principle 2"
      - domain: power
        memory_items:
          - "Power principle 1"
```

## Components

- **pdf_reader.py**: Extracts text from PDFs (supports PyPDF2, pdfplumber, or .txt files)
- **chapter_builder.py**: Splits text into chapters using heuristics
- **domain_classifier.py**: Classifies chapters into domains (15 fixed domains)
- **memory_extractor.py**: Extracts memory items using keyword matching
- **book_aggregator.py**: Combines all data into final structure
- **persist_book.py**: Saves to YAML with validation
- **ingest.py**: Main orchestrator

## Domains

The system uses 15 fixed domains:

1. grand_strategy
2. power
3. optionality
4. psychology
5. diplomacy
6. conflict
7. truth
8. risk
9. timing
10. data_judgment
11. operations
12. technology
13. adaptation
14. legitimacy
15. narrative

## Requirements

- Python 3.7+
- Optional: `PyPDF2` or `pdfplumber` for PDF parsing (falls back to .txt files if not available)
- Optional: `pyyaml` for YAML output (falls back to JSON if not available)

## Installation

```bash
# Install optional dependencies for better PDF support
pip install PyPDF2  # or pdfplumber
pip install pyyaml
```

## Status

✅ **Fully Operational**

- All components implemented
- Duplicate code issues fixed
- CLI entry point available
- Schema validation in place
- Error handling and progress reporting

