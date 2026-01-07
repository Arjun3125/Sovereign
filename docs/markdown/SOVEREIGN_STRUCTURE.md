# Sovereign: Domain-Pure Minister Council System

**Lock this structure in place.**

```
sovereign/
├── embedding/
│   ├── embedder.py (not needed - using embedding_gatekeeper)
│   ├── hash_registry.py (anti-duplication)
│   ├── domain_vector_manager.py (FAISS per-domain stores)
│   └── embedding_gatekeeper.py (main ingestion gate)
├── retrieval/
│   ├── minister_retriever.py (minister-domain restricted)
│   ├── council_runner.py (run all ministers)
│   └── tribunal.py (verdict logic)
├── config/
│   ├── domains.py (15 domain → FAISS index map)
│   ├── ministers.py (15 ministers → domain list)
│   └── thresholds.py (disagreement, confidence floors)
├── data/
│   ├── doctrine_units.json (source doctrines)
│   └── embedded_hashes.json (anti-duplication registry)
├── models/
│   └── embedding_client.py (Ollama wrapper)
└── vector_store/
    └── *.index + *.index.meta.json (FAISS + metadata)
```

## Key Properties

✅ **Deterministic**: Same input → same embedding (via Ollama)  
✅ **Domain-Pure**: Each domain has isolated FAISS store  
✅ **Minister-Restricted**: Each minister only sees its domain doctrines  
✅ **Anti-Duplication**: Hash registry blocks re-embedding  
✅ **Restart-Safe**: Embeddings are immutable once written  
✅ **No Hallucination**: Every doctrine sourced from doctrine_units.json  
✅ **Sovereign-First**: Tribunal + Silence format decisions

## Usage

**Embed doctrines:**
```bash
python sovereign_cli.py embed --input sovereign/data/doctrine_units.json
```

**Query council:**
```bash
python sovereign_cli.py query "What should I do about X"
python sovereign_cli.py query "Should I move fast?" --minister "Minister of Timing"
```

**Tribunal triggers on:**
- Disagreement > 35% (confidence spread)
- Any minister < 30% confidence → ESCALATE
- All ministers < 40% confidence → SILENCE
- Otherwise → ALLOW

## Files

- `sovereign/embedding/hash_registry.py`: Registry to block re-embedding
- `sovereign/embedding/domain_vector_manager.py`: FAISS store per domain
- `sovereign/embedding/embedding_gatekeeper.py`: Main ingestion (dedup + embed + store)
- `sovereign/retrieval/minister_retriever.py`: Minister-restricted retrieval
- `sovereign/retrieval/council_runner.py`: Run all ministers in parallel
- `sovereign/retrieval/tribunal.py`: Verdict engine (ALLOW/SILENCE/ESCALATE)
- `sovereign/models/embedding_client.py`: Ollama HTTP wrapper
- `sovereign/config/domains.py`: 15 domains → FAISS paths
- `sovereign/config/ministers.py`: 15 ministers → domain lists
- `sovereign/config/thresholds.py`: Confidence gates
- `sovereign_cli.py`: CLI entry point

## No Hallucination Path

```
doctrine_units.json
    ↓
hash_registry (dedup check)
    ↓
embedding_client (Ollama)
    ↓
domain_vector_manager (FAISS)
    ↓
minister_retriever (domain-restricted)
    ↓
council_runner (all ministers)
    ↓
tribunal (ALLOW/SILENCE/ESCALATE)
```

**Sovereign always has final say. System does not act on council advice.**
