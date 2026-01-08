# Cold Strategist - End-to-End Ingestion Pipeline Map

## Overview
The ingestion pipeline processes books through structured phases, extracting doctrine and storing it for retrieval.

---

## Pipeline Entry Points

### 1. **CLI Entry** (Primary)
```
cold_strategist/scripts/ingest_all_books.py
↓
Uses: cold_strategist.ingest_v2.ingest_v2 import ingest_v2
```

### 2. **Direct API Entry**
```python
from cold_strategist.ingest_v2.ingest_v2 import ingest_v2

result = ingest_v2(
    book_text="...",
    book_id="art_of_war",
    output_dir="v2_store"
)
```

### 3. **Ingestion Module Entry**
```python
from cold_strategist.ingestion.ingest import ingest_book
ingest_book(pdf_path="file.pdf", book_id="book_id")
```

---

## Phase-1: Book Structuring → Chapter Extraction

### Files Involved:
- `cold_strategist/ingest_v2/ingest_v2.py` — **Main orchestrator**
  - Coordinates Phase-1 and Phase-2
  - Handles progress tracking
  - Resume-safe ingestion

- `cold_strategist/ingest_v2/phase1_structure.py` — **LLM-based structuring**
  - Calls LLM to extract chapters from raw text
  - Validates chapter structure
  - Returns: `{chapters: [{chapter_index, chapter_title, chapter_text}, ...]}`

- `cold_strategist/ingest_v2/prompts.py` — **LLM Prompts**
  - Phase-1 system prompt
  - Phase-1 user prompt template

- `cold_strategist/ingest_v2/llm_client.py` — **LLM Interface**
  - `call_llm(prompt, model)` — Calls Ollama
  - Handles streaming responses
  - JSON parsing

### Flow:
```
Input: Raw book text (70K-1.5M characters)
         ↓
    [LLM Call via ollama]
         ↓
    Phase-1 extracts chapters
         ↓
    validate_phase1() checks schema
         ↓
    Output: Chapter list {chapters: [...]}
```

---

## Phase-2: Doctrine Extraction from Chapters

### Files Involved:
- `cold_strategist/ingest_v2/phase2_doctrine.py` — **Doctrine extractor**
  - For each chapter: calls LLM to extract doctrine
  - Validates doctrine schema
  - Returns: `{doctrine: [...], principles: [...]}`

- `cold_strategist/ingest_v2/prompts.py` — **Phase-2 prompts**
  - Doctrine extraction system prompt
  - Doctrine user prompt template

- `cold_strategist/ingest_v2/validators.py` — **Schema validators**
  - `validate_phase1()` — Validates chapter structure
  - `validate_phase2()` — Validates doctrine output
  - Raises `ValidationError` on mismatch

- `cold_strategist/ingest_v2/progress.py` — **Progress tracking**
  - Tracks which chapters are done
  - Enables resume-safe ingestion

### Flow:
```
For each chapter:
    Input: Chapter text
           ↓
      [LLM Call via ollama]
           ↓
      Phase-2 extracts doctrine
           ↓
      validate_phase2() checks schema
           ↓
    Save chapter_XX.json to output_dir
           ↓
    Update progress tracking
           ↓
    Output: {chapter_index, doctrine, principles}
```

---

## Storage & Persistence

### Files Involved:
- `cold_strategist/storage/books/` — **Doctrine storage**
  - `<book_id>/raw_chapters/` — Raw chapter text
  - `<book_id>/doctrine_chapters/` — Extracted doctrine (JSON)

### Persist Functions:
```python
# In ingest_v2.py:
with open(chapter_path, "w", encoding="utf-8") as f:
    json.dump(doctrine, f, indent=2, ensure_ascii=False)
```

---

## Quality Assurance & Validation

### Files Involved:
- `cold_strategist/audit/detect.py` — **Conflict detection**
  - Detects contradictions in doctrine
  - Cross-references between chapters

- `cold_strategist/audit/normalize.py` — **Doctrine normalization**
  - Standardizes doctrine format
  - Removes duplicates

- `cold_strategist/audit/pairwise.py` — **Pairwise comparison**
  - Compares doctrine entries
  - Finds semantic similarity

- `cold_strategist/audit/report.py` — **Audit reporting**
  - Generates audit reports
  - Summarizes findings

### Post-Ingest Validation:
```
cold_strategist/scripts/post_ingest_validation.py
├── check_completion()
├── duplicate_embedding_sanity()
├── vector_store_integrity()
├── ledger_consistency()
├── principle_schema_validation()
└── simple_spot_check_queries()
```

---

## Alternative Pipeline: doctrine_ingestion/

### Entry Point:
```python
from cold_strategist.ingestion.ingest import ingest_book
ingest_book(pdf_path="file.pdf", book_id="book_id")
```

### Key Modules:
- `cold_strategist/ingestion/ingest.py` — Main orchestrator
- `cold_strategist/ingestion/pdf_reader.py` — PDF extraction
- `cold_strategist/ingestion/chapter_detector.py` — Chapter splitting
- `cold_strategist/ingestion/chapter_processor.py` — Process chapters
- `cold_strategist/ingestion/assembler.py` — Assemble final structure
- `cold_strategist/ingestion/validator.py` — Schema validation
- `cold_strategist/ingestion/storage.py` — Save to storage
- `cold_strategist/ingestion/parallel_ingest.py` — Parallel processing
- `cold_strategist/ingestion/recovery.py` — Recovery from failures

---

## Configuration & Utilities

### Files Involved:
- `cold_strategist/ingest_v2/model_map.py` — Model configurations
- `cold_strategist/ingest_v2/retry_controller.py` — Retry logic
- `cold_strategist/ingest_v2/schemas.py` — Data schemas
- `cold_strategist/ingest_v2/yaml_schema.py` — YAML schema definitions

---

## Full End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: 9 Books from cold_strategist/workspace/              │
│  • The_Art_Of_War/00_raw_text.txt (70K chars)               │
│  • THE 48 LAWS OF POWER/ (1.4M chars)                       │
│  • ... (7 more books)                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  ingest_all_books.py        │
        │  (Main orchestrator)        │
        └──────────┬──────────────────┘
                   │
        For each book:
        ┌──────────────────────────────────────┐
        │ 1. Load raw text from workspace      │
        │ 2. Call ingest_v2()                  │
        └──────────────────┬───────────────────┘
                           │
                ┌──────────▼──────────┐
                │  PHASE-1: Structure │
                │  phase1_structure.py│
                └──────────┬──────────┘
                           │
                    ┌──────▼───────┐
                    │ call_llm()   │
                    │ Ollama       │
                    │ qwen model   │
                    └──────┬───────┘
                           │
                    ┌──────▼──────────────┐
                    │ Extract chapters    │
                    │ validate_phase1()   │
                    └──────┬──────────────┘
                           │
                ┌──────────▼───────────────┐
                │  PHASE-2: Doctrine      │
                │  phase2_doctrine.py     │
                └──────────┬──────────────┘
                           │
                  For each chapter:
                  ┌──────────▼──────────┐
                  │ call_llm()          │
                  │ Extract doctrine    │
                  │ validate_phase2()   │
                  └──────────┬──────────┘
                             │
                    ┌────────▼────────┐
                    │ Save to storage │
                    │ v2_store/       │
                    └────────┬────────┘
                             │
                    ┌────────▼──────────┐
                    │ Update progress   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼────────────┐
                    │ Final checks        │
                    │ Validation, audit   │
                    │ Generate report     │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼──────────┐
                    │ OUTPUT:            │
                    │ v2_store/          │
                    │ • <book_id>/       │
                    │   - structure.json │
                    │   - 01.json        │
                    │   - 02.json        │
                    │   - ...            │
                    │ • ingest_report.json
                    └────────────────────┘
```

---

## Test Coverage

### Ingestion Tests:
- `tests/test_ingestion_master.py` — Full pipeline
- `tests/test_assembly_master.py` — Assembly validation
- `tests/test_embedding_master.py` — Embedding tests
- `tests/test_cli_api_master.py` — CLI/API interface

### Validation Tests:
- `tests/test_b1_no_duplicate_embeddings.py`
- `tests/test_b2_embedding_stability.py`
- `tests/test_c1_cross_reference_integrity.py`
- `tests/test_c2_assembly_reversibility.py`

---

## Key Statistics

| Component | Files | Lines |
|-----------|-------|-------|
| **ingest_v2/** | 35 | 5000+ |
| **ingestion/** | 14 | 4000+ |
| **storage/** | 1 | N/A (data) |
| **audit/** | 5 | 3000+ |
| **scripts/** | 5 | 2000+ |
| **Total** | ~60 | 14000+ |

---

## Configuration

### Environment Variables:
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

### Workspace Location:
```
cold_strategist/workspace/
├── The_Art_Of_War/
│   ├── 00_raw_text.txt
│   └── metadata/
├── THE 48 LAWS OF POWER 06/
├── The Laws of Human Nature/
└── ... (6 more)
```

### Output Location:
```
v2_store/
├── art_of_war/
│   ├── structure.json (Phase-1 output)
│   ├── 01.json ... 35.json (Phase-2 chapters)
├── 48_laws_of_power/
└── ... (other books)
```

---

## Summary

**Total Ingestion Files in cold_strategist: ~60 files**

- **Entry Points:** `ingest_all_books.py`, `ingest_v2.py`, `ingest_book.py`
- **Core Phases:** `phase1_structure.py`, `phase2_doctrine.py`
- **Support:** LLM client, validators, storage, progress tracking
- **Quality:** Audit, validation, reporting
- **Testing:** 40+ test files covering all layers

**All files are organized under cold_strategist namespace and use clean imports via:
```python
from cold_strategist.ingest_v2 import ingest_v2
from cold_strategist.ingestion import ingest_book
from cold_strategist.audit import detect_conflicts
```
