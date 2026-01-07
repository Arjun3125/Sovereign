# Sovereign Workspace - Naming Conflict & Duplication Analysis

**Generated:** December 31, 2025

---

## Executive Summary

The Sovereign workspace contains **extensive duplication** with the same task names, class names, and functions across multiple locations. This analysis identifies:

- **CRITICAL DUPLICATES** - Classes and functions defined in >2 locations
- **ACTIVE vs INACTIVE** - Which implementations are actually used
- **LEGACY CODE** - Outdated duplicates that should be removed
- **MIGRATION PATHS** - Where to consolidate code

---

## 1. MAIN ENTRY POINTS (23 duplicates)

### `def main()` - Located in 23 files

| Location | Status | Purpose | Used? |
|----------|--------|---------|-------|
| `cli/main.py` | ✅ ACTIVE | CLI entry point | YES |
| `cold_strategist/cli/main.py` | ✅ ACTIVE | Cold Strategist CLI | YES |
| `cold_strategist/app/main.py` | ❓ UNKNOWN | App entry | MAYBE |
| `app/main.py` | ❓ UNKNOWN | App entry | MAYBE |
| `tests/run_l*.py` (5 files) | ✅ ACTIVE | Test runners | YES |
| `tests/run_all_layers.py` | ✅ ACTIVE | Test coordinator | YES |
| `scripts/ingest_book_v2_full.py` | ✅ ACTIVE | Ingest pipeline | YES |
| `scripts/run_principles_batch.py` | ✅ ACTIVE | Batch processor | YES |
| `tests/dry_run_ingest.py` | ✅ ACTIVE | Test pipeline | YES |
| `cold_strategist/cli/dashboards.py` | ✅ ACTIVE | Dashboard CLI | YES |
| `cold_strategist/scripts/ingest_books.py` | ⚠️  LEGACY | Old ingest | NO |
| `scripts/ingest_books.py` | ⚠️  LEGACY | Old ingest | NO |
| `cli/*.py` (3 files) | ⚠️  LEGACY | Old ingest | NO |
| `tests/tmp_*.py` (3 files) | ⚠️  TEMP | Temporary tests | NO |
| `tests/ingest_v2_phase*.py` (2 files) | ⚠️  LEGACY | Old phases | NO |

**Recommendation:** Consolidate CLI entry points to `cold_strategist/cli/main.py`. Remove legacy `cli/` and old `scripts/ingest_*.py` files.

---

## 2. CONTEXT & STATE CLASSES (Multiple Definitions)

### `class Context` - 4 Definitions

| Location | Version | Fields | Used? |
|----------|---------|--------|-------|
| `cold_strategist/cli/prompts.py` | ✅ ACTIVE | `domain`, `stakes`, `urgency`, `fatigue` | YES - CLI collection |
| `cold_strategist/context/context_schema.py` | ✅ ACTIVE | `DecisionContext` dataclass | YES - Internal model |
| `cli/prompts.py` | ⚠️  LEGACY | Old schema | NO |
| `context/context_schema.py` | ⚠️  LEGACY | Old schema | NO |

**Issue:** Two different "Context" implementations - CLI collection vs internal data model (confusing naming).

**Recommendation:**
- Rename `prompts.Context` → `CliContext` (avoids confusion)
- Use `DecisionContext` for internal representation
- Update imports in `cold_strategist/cli/main.py`

### `class State` - 4 Definitions

| Location | Fields | Status |
|----------|--------|--------|
| `cold_strategist/cli/prompts.py` | User state collection | ✅ ACTIVE |
| `cold_strategist/context/context_schema.py` | DecisionState dataclass | ✅ ACTIVE |
| `cli/prompts.py` | Old version | ⚠️  LEGACY |
| `context/context_schema.py` | Old version | ⚠️  LEGACY |

**Same issue as Context** - two different concepts with same name.

---

## 3. PATTERN CLASS (Multiple Definitions)

### `class Pattern` - 3 Definitions

| Location | Purpose | Status | Used? |
|----------|---------|--------|-------|
| `cold_strategist/core/memory/pattern_engine.py` | War pattern detection | ✅ ACTIVE | YES |
| `cold_strategist/context/context_schema.py` | Pattern dataclass | ✅ ACTIVE | YES |
| `TECHNICAL_SPEC.md` (specs only) | Documentation | 📄 DOCS | NO |

**Status:** Intentional - different purposes, both active. No consolidation needed but update docs.

---

## 4. ORCHESTRATOR FUNCTIONS (Duplicates)

### `def route()` - 3 Locations

| Location | Signature | Status |
|----------|-----------|--------|
| `cold_strategist/core/orchestrator/router.py` | `route(mode: str) -> Callable` | ✅ ACTIVE |
| `core/orchestrator/router.py` | Old version | ⚠️  LEGACY |
| `TECHNICAL_SPEC.md` | Specification | 📄 DOCS |

**Recommendation:** Remove `core/orchestrator/router.py`. Use only `cold_strategist/core/orchestrator/router.py`.

### `def run_analysis()` - 2 Locations

| Location | Version | Status |
|----------|---------|--------|
| `cold_strategist/core/orchestrator/engine.py` | Updated | ✅ ACTIVE |
| `core/orchestrator/engine.py` | Old | ⚠️  LEGACY |

**Recommendation:** Remove `core/orchestrator/engine.py`.

### `def route_calibration()` - 2 Locations

| Location | Status |
|----------|--------|
| `cold_strategist/core/orchestrator/router.py` | ✅ ACTIVE |
| `core/orchestrator/router.py` | ⚠️  LEGACY |

---

## 5. RENDER/OUTPUT FUNCTIONS

### `def render_verdict()` - 2 Locations

| Location | Status |
|----------|--------|
| `cold_strategist/cli/render.py` | ✅ ACTIVE |
| `cli/render.py` | ⚠️  LEGACY |

**Recommendation:** Remove `cli/render.py`.

---

## 6. LOGGING UTILITIES

### `setup_logging()` & `get_logger()` - Deprecated Shims

| Module | Status | Issue |
|--------|--------|-------|
| `utils/logging.py` | ⚠️  DEPRECATED | Shadows stdlib `logging` |
| `utils/sovereign_logging.py` | ✅ ACTIVE | Correct implementation |
| `cold_strategist/utils/logging.py` | ⚠️  DEPRECATED | Shadows stdlib `logging` |
| `cold_strategist/utils/sovereign_logging.py` | ✅ ACTIVE | Correct implementation |

**Recommendation:** Delete both `logging.py` shims. Update all imports to use `sovereign_logging`.

---

## 7. PROGRESS TRACKING (Multiple Implementations)

### Progress Functions - 4-5 Implementations

| Location | Purpose | Status | Overlap |
|----------|---------|--------|---------|
| `utils/progress_core.py` | Hash-based dedup | ✅ ACTIVE | Core logic |
| `utils/progress_display.py` | Display summary | ✅ ACTIVE | UI |
| `utils/progress.py` | Wrapper/aggregator | ❓ UNKNOWN | Possible duplicate |
| `utils/monitor_progress.py` | Terminal UI | ⚠️  LEGACY | Old version |
| `utils/metrics.py` | Metrics collection | ✅ ACTIVE | Related but different |

**Recommendation:** Audit `progress.py` vs `progress_core.py` for actual duplication.

---

## 8. EMBEDDING/HASHING UTILITIES

### Hash Functions - Duplicated Logic

| Location | Function | Status |
|----------|----------|--------|
| `utils/hash.py` | `stable_hash()`, `chunk_hash()` | ✅ ACTIVE |
| `utils/embedding_guard.py` | `validate_hash_schema()` | ✅ ACTIVE |
| Multiple ingest files | Inline implementations | ⚠️  SCATTERED |

**Recommendation:** Ensure all ingest code uses `utils/hash.py` functions, not reimplemented logic.

---

## 9. MINISTER CLASSES (Expected Duplication)

### `class MinisterOf*` - Intentional in Two Locations

| Location | Status | Purpose |
|----------|--------|---------|
| `tribunal/ministers.py` | ⚠️  OLD | Original tribunal pattern |
| `cold_strategist/ministers/*.py` | ✅ ACTIVE | War-aware ministers |

**Status:** This IS intentional - old vs new implementation. Keep both as different phases but eventually migrate fully to `cold_strategist/ministers/`.

### Min Minister Count: 10+ individual ministers across locations

- Old: `MinisterOfTruth`, `MinisterOfRisk`, `MinisterOfPower`, `MinisterOfOptionality`
- New: Expanded to `Discipline`, `Diplomacy`, `Data`, `Conflict`, `Psychology`, `Power`, `Strategy`, `Timing`, `Technology`, `Adaptation`, `Legitimacy`, `Optionality`

---

## 10. INGEST PIPELINES (Major Duplication)

### Ingest Functions - Multiple Versions

| Location | Version | Status | Last Used |
|----------|---------|--------|-----------|
| `ingest_v2/` | v2 (active) | ✅ ACTIVE | Current |
| `doctrine_ingestion/` | Modern | ✅ ACTIVE | Current |
| `cli/ingest_cli.py` | v1 | ⚠️  LEGACY | Old |
| `scripts/ingest_*.py` | v1-v2 | ⚠️  LEGACY | Unclear |
| `_legacy_ingest/` | v0 | 🗑️  JUNK | Archived |
| `cold_strategist/_legacy_ingest/` | v0 | 🗑️  JUNK | Archived |

**Recommendation:** 
1. Decide on **single ingest entry point**
2. Archive v1 to `_legacy_ingest/`
3. Use either `ingest_v2/` or `doctrine_ingestion/` (not both)
4. Clean up `scripts/` ingest files

---

## 11. TEST FILES (Multiple Frameworks)

### Test Structure Duplication

| Location | Framework | Status |
|----------|-----------|--------|
| `tests/unit/` | pytest | ✅ ACTIVE |
| `tests/` (root level) | unittest/custom | ✅ ACTIVE |
| `tests/debate/` | unittest | ✅ ACTIVE |
| `tests/modes/` | unittest | ✅ ACTIVE |
| `tests/e2e/` | unittest | ✅ ACTIVE |
| `tests/memory/` | unittest | ✅ ACTIVE |
| `cold_strategist/tests/` | unittest | ✅ ACTIVE |
| `tribunal/` test files | Custom | ⚠️  SCATTERED |

**Issue:** Mixed pytest and unittest frameworks. Inconsistent test organization.

**Recommendation:** 
1. Standardize on pytest
2. Reorganize to `tests/` with clear layer structure (L1-L5)
3. Remove `cold_strategist/tests/` - consolidate to root `tests/`

---

## 12. CONFIG FILES (Multiple Schemas)

| Location | Content | Status |
|----------|---------|--------|
| `config/llm.yaml` | LLM config | ✅ ACTIVE |
| `config/` (root) | Various | ❓ UNCLEAR |
| `cold_strategist/config/llm.yaml` | LLM config | ✅ ACTIVE |
| `doctrine/schema.yaml` | Doctrine schema | ✅ ACTIVE |
| `ingest_v2/yaml_schema.py` | Schema code | ✅ ACTIVE |

**Recommendation:** Centralize config loading. Choose single authority for `llm.yaml`.

---

## 13. QUERY ENGINE DUPLICATES

| Location | Status | Purpose |
|----------|--------|---------|
| `query_engine/` (root) | ⚠️  LEGACY | Old retrieval |
| `cold_strategist/query/` | ✅ ACTIVE | War-aware queries |
| `tribunal/` ask functions | ⚠️  SCATTERED | Query interface |

**Recommendation:** Consolidate to `cold_strategist/query/`.

---

## 14. KNOWLEDGE BASE DUPLICATES

| Location | Status | Purpose |
|----------|--------|---------|
| `knowledge/` (root) | ⚠️  LEGACY | Book knowledge store |
| `cold_strategist/knowledge/` | ✅ ACTIVE | War-aware knowledge |
| `doctrine/` | ✅ ACTIVE | Doctrine storage |
| `books/` | ✅ ACTIVE | Raw book data |

**Status:** These serve different purposes (OK), but verify imports use correct version.

---

## 15. RAG SYSTEM DUPLICATES

| Location | Status |
|----------|--------|
| `rag/` (root) | ⚠️  LEGACY |
| `cold_strategist/core/knowledge/war_aware_rag_retriever.py` | ✅ ACTIVE |
| `cold_strategist/rag/` | Likely duplicated | ⚠️  CHECK |
| `rag_store/` | Storage layer | ✅ ACTIVE |

**Recommendation:** Audit `rag/` vs `cold_strategist/core/knowledge/war_aware_rag_retriever.py` for actual duplication.

---

## 16. MEMORY/STATE MANAGEMENT (Expected Variation)

| Location | Purpose | Status |
|----------|---------|--------|
| `cold_strategist/core/memory/` | Modern event store | ✅ ACTIVE |
| `cold_strategist/state/` | State serialization | ✅ ACTIVE |
| `memory/` (root) | Old store | ⚠️  LEGACY |
| `state/` (root) | Old state | ⚠️  LEGACY |

---

## 17. DEBATE SYSTEM DUPLICATES

| Location | Purpose | Status |
|----------|---------|--------|
| `debate/` (root) | Original debate engine | ⚠️  LEGACY |
| `cold_strategist/core/debate/` | War-aware debate | ✅ ACTIVE |
| `tribunal/debate.py` | Tribunal interface | ⚠️  SCATTERED |
| `core/debate/` | Old version | ⚠️  LEGACY |

---

## SUMMARY: CONSOLIDATION PRIORITY

### 🔴 HIGH PRIORITY (Remove Immediately)

```
❌ cli/                          → Use cold_strategist/cli/
❌ core/orchestrator/            → Use cold_strategist/core/orchestrator/
❌ utils/logging.py              → Use utils/sovereign_logging.py
❌ cold_strategist/utils/logging.py → Use cold_strategist/utils/sovereign_logging.py
❌ _legacy_ingest/               → Move to archive/
❌ cold_strategist/_legacy_ingest/ → Move to archive/
❌ scripts/ingest_*.py (legacy)  → Consolidate or archive
```

### 🟡 MEDIUM PRIORITY (Refactor)

```
⚠️  Context/State naming in cli/prompts.py  → Rename to CliContext/CliState
⚠️  query_engine/                           → Consolidate to cold_strategist/query/
⚠️  knowledge/ (root)                       → Consolidate to cold_strategist/knowledge/
⚠️  rag/ (root)                             → Audit vs war_aware_rag_retriever
⚠️  Test framework mix (pytest + unittest)  → Standardize on pytest
```

### 🟢 LOW PRIORITY (Monitor)

```
✅ Pattern class (pattern_engine.py)      → Different purposes, OK
✅ Ministers old vs new                   → Expected evolution, OK
✅ Different knowledge domains            → Different purposes, OK
```

---

## ACTIONABLE CLEANUP CHECKLIST

- [ ] **Phase 1:** Remove deprecated logging modules
- [ ] **Phase 2:** Delete `cli/` folder (use `cold_strategist/cli/`)
- [ ] **Phase 3:** Delete `core/orchestrator/` (use `cold_strategist/core/orchestrator/`)
- [ ] **Phase 4:** Archive legacy ingest files
- [ ] **Phase 5:** Consolidate query engine
- [ ] **Phase 6:** Standardize test framework to pytest
- [ ] **Phase 7:** Rename CLI context/state to avoid confusion
- [ ] **Phase 8:** Document which implementation is canonical for each function

---

## Files to DELETE or MOVE

### Delete (no longer used):
```
cli/__init__.py
cli/main.py
cli/render.py
cli/prompts.py
cli/args.py
core/orchestrator/*.py
utils/logging.py
cold_strategist/utils/logging.py
scripts/ingest_*.py (v1-v2 legacy)
```

### Move to `_archived/`:
```
_legacy_ingest/
cold_strategist/_legacy_ingest/
tests/tmp_*.py
tests/ingest_v2_phase*.py
query_engine/ (or consolidate)
```

---

**Total Duplicates Identified:** 40+
**Critical Issues:** 8
**Files to Cleanup:** 20+

