# IMMEDIATE TODO - HARDENING PHASE COMPLETION

## Current State
✅ All 6 critical violations FIXED in knowledge_debate_engine.py
✅ All 7 unit tests PASSING
✅ Dataclasses updated with new fields
✅ Methods refactored to use structured output
✅ No narrative tone, deduplication tracking, explicit stances, Truth violations, TribunalVerdict, ConflictEvent typed

## Blocking Issue
⚠️ MinisterSynthesizer prompt NOT YET UPDATED
- Synthesis still outputs old schema
- New _minister_position() expects: stance, justification, violations, doctrine_ids, constraints
- Without this, the hardened engine cannot receive properly structured input

## NEXT STEPS (In Order)

### TASK 1: Update MinisterSynthesizer Prompt (CRITICAL)
**File**: `cold_strategist/core/knowledge/synthesize/minister_synthesizer.py`
**Action**: Update prompt to enforce new output schema
**Output format needed**:
```python
{
    "stance": "ADVANCE",  # Only: ADVANCE|DELAY|AVOID|CONDITIONAL
    "justification": "Doctrine A, Doctrine B; because...",  # NO narrative phrases
    "doctrine_ids": ["doc1", "doc2"],  # For deduplication
    "violations": [],  # Truth only: ["Claim X contradicts Doctrine Y"]
    "constraints": ["Monitor outcomes"],
    "confidence_score": 0.75
}
```

**Prompt update needed**:
- Remove any request for narrative
- Add explicit: "Output ONLY doctrine references, no narrative phrases"
- Add: "Extract violations ONLY if you are Truth minister"
- Add: "List doctrine_ids so caller can deduplicate"

### TASK 2: Verify _minister_position() Reads New Schema
**File**: `cold_strategist/debate/knowledge_debate_engine.py`
**Action**: Confirm it properly extracts stance, justification, violations, doctrine_ids
**Check**:
- synthesis.get("stance") → position.stance
- synthesis.get("justification") → sanitize → position.justification
- synthesis.get("doctrine_ids") → deduplicate → position.unique_doctrines
- synthesis.get("violations") → position.violations (trigger STOP if present)

### TASK 3: End-to-End Test
**File**: Run a full debate with hardened engine
**Verify**:
- No narrative in final output
- Unique doctrines counted (not duplicates)
- ConflictEvent typed (not just confidence gaps)
- TribunalVerdict structured (not string)
- format_debate_transcript() shows all structure

### TASK 4: Integration into CLI (if needed)
**File**: `sovereign_cli.py`
**Action**: Update query display to show new output format
**Show**:
- Unique doctrines per minister
- Conflict types + severity
- Tribunal verdict decision + constraints

---

## DO NOT DO (until hardening locked in)
❌ Add new features
❌ Change tribunal logic further
❌ Modify verdict constraints
❌ Add new conflict types
❌ Change stance definitions

---

## Status Indicators

Once complete:
- [ ] MinisterSynthesizer prompt updated
- [ ] End-to-end test runs without error
- [ ] Output shows structured conflicts, verdicts, unique doctrines
- [ ] No narrative language in output
- [ ] Tribunal constraints enforced in final verdict
- [ ] Truth violations trigger STOP
- [ ] Ready for user acceptance

---

## Files Touched This Session

**Modified**:
- `cold_strategist/debate/knowledge_debate_engine.py` (712 lines) - All 6 fixes applied

**Tests**:
- `test_hardening_units.py` - 7/7 PASS
- `test_hardening_fixes.py` - Created (requires full imports)

**Documentation**:
- `HARDENING_COMPLETION.md` - Full summary
- `IMMEDIATE_TODO.md` - This file

---

## Quick Validation

Run to verify no regressions:
```bash
python test_hardening_units.py
```

Expected: 7/7 PASS, showing all 6 issues validated

---

**Target**: MinisterSynthesizer prompt update + end-to-end test by end of next task
