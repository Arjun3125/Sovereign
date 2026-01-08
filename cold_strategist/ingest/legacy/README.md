LEGACY INGEST IMPLEMENTATIONS

These files are preserved for:
- audit
- reproducibility
- migration

DO NOT import these modules directly from canonical code.

All canonical ingest access MUST go through:

cold_strategist.ingest.pipeline

Notes:
- These files may contain LLM-driven implementations and experimental code.
- Do not add new logic here. If you must modify for migration, copy into canonical facades.
