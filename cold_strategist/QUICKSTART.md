# Quick Start - Cold Strategist Examples

## Installation

No external dependencies beyond Python standard library + existing project structure.

```bash
cd cold_strategist
```

## Example 1: War Mode - Negotiation

Scenario: You're in a high-stakes negotiation with unfavorable deadline pressure.

```bash
python cold.py war \
  --domain negotiation \
  --arena career \
  --stakes high \
  --urgency 0.8 \
  --constraints reversible minimal_collateral legal
```

**When prompted:**
```
Describe the situation:
> Counterparty demands contract signature by EOD. Their terms heavily favor them.
> I have 2 weeks to renegotiate but they're pressuring immediate decision.
> My job security depends on this deal, but signing bad terms is career-limiting.
```

**Expected Output:**

```
======================================================================
VERDICT
======================================================================

PROCEED WITH CAUTION

Primary Move:
  Request call with counterparty VP to discuss timeline extension.
  Present alternative timeline: 5 business days for final review.
  Highlight mutual benefit: thorough due diligence reduces future disputes.

Posture: conditional

Risk: ▓▓▓▓▓░░░░░ 48.0%

Reversible: Yes
Optionality: preserved

Alternatives:
  1. Accept and document exceptions in side letter
  2. Walk away and seek alternative partnership

DO NOT:
  ✗ Accept artificial deadline (escalation tactic)
  ✗ Sign without legal review of debt clauses
  ✗ Make emotional arguments (strengthens their position)
  ✗ Reveal your time pressure

Next Step:
  Email counterparty within 2 hours requesting 30-min call

----------------------------------------------------------------------
Event ID (save for outcome resolution): a3f7c2e1-9b4d-4a2c-8f1d-2b5e6c0f
----------------------------------------------------------------------
```

**Save the Event ID!** You'll need it later to log how this actually turned out.

---

## Example 2: War Mode with Pattern Analysis

If you've made similar decisions before, see what patterns exist:

```bash
python cold.py war \
  --domain career \
  --arena negotiation \
  --stakes high \
  --analyze-patterns
```

**Additional Output (if history exists):**

```
======================================================================
DETECTED PATTERNS
======================================================================

• war_escalation_bias
  Type: war_pattern
  Frequency: 3
  Domain: war
  Last Outcome: failure

• war_false_urgency_loop
  Type: war_pattern
  Frequency: 2
  Domain: war
  Last Outcome: failure

======================================================================
N'S ADJUSTED POSTURE
======================================================================

Posture: heightened caution on escalation; skepticism toward urgency claims

Caution: ⬆ 0.70x (30% more cautious on escalation)
Urgency Threshold: ⬆ 1.50x (require 50% more evidence for urgency)
Bluntness: → 1.00x (unchanged)

======================================================================
LEARNING SUMMARY
======================================================================

WAR LEARNING (6 war events):

• Events: 6
• Patterns detected: 2
• Pattern insights:
  - war_escalation_bias (freq 3)
  - war_false_urgency_loop (freq 2)

N's Adjusted Posture:
  heightened caution on escalation; skepticism toward urgency claims
```

This shows N is adjusting based on past outcomes. Next time you face similar urgency pressure, N will be more skeptical.

---

## Example 3: Normal Mode

For standard counsel (not adversarial):

```bash
python cold.py normal \
  --domain career \
  --stakes medium \
  --emotional-load 0.6
```

**When prompted:**
```
Describe the situation:
> Considering accepting a promotion that requires relocation.
> Family doesn't want to move. I'm torn between career growth and stability.
```

**Output:**
Standard counsel (ministers' advice, N's synthesis).

---

## Example 4: Resolve an Outcome (days later)

Days after your negotiation decision, now you know what happened.

```bash
python cold_outcome.py a3f7c2e1-9b4d-4a2c-8f1d-2b5e6c0f --mode war
```

**When prompted:**
```
Outcome result (success | partial | failure):
> partial

Actual damage incurred (0.0-1.0):
> 0.35

Benefit gained (0.0-1.0):
> 0.72

Lessons learned (comma-separated, or press Enter to skip):
> Counterparty backed down after 2 calls, Extended timeline bought us due diligence
> space, Final terms were 70% better than original, Relationship maintained
```

**Output:**

```
======================================================================
OUTCOME RESOLVED
======================================================================

Event ID: a3f7c2e1-9b4d-4a2c-8f1d-2b5e6c0f
Outcome: partial
Damage: 0.35
Benefit: 0.72

======================================================================
LEARNING SUMMARY
======================================================================

WAR LEARNING (7 war events):

• Events: 7
• Patterns detected: 2
• Pattern insights:
  - war_escalation_bias (freq 3)
  - war_false_urgency_loop (freq 2)

N's Adjusted Posture:
  heightened caution on escalation; skepticism toward urgency claims
```

Now the system has learned from this outcome. The escalation bias pattern is still there (your caution is still elevated), but N saw that this decision had a good outcome (0.72 benefit), so patterns may persist but N's confidence in avoiding escalation is validated.

---

## Example 5: Fictional War Scenario

War mode works for fiction/games too:

```bash
python cold.py war \
  --domain fictional \
  --arena fictional \
  --stakes high \
  --constraints reversible legal
```

**When prompted:**
```
Describe the situation:
> Fantasy RPG: Our party needs to negotiate with the dragon hoard-keeper
> to access a mountain pass. They're suspicious and territorial.
> We need to get through in 2 days before enemy reinforcements arrive.
```

**Output:**
War analysis for a fictional scenario. Safe, no real harm, but exercises strategic thinking.

---

## Example 6: Multiple Decisions Over Time

You can log many decisions and watch learning accumulate:

**Day 1:**
```bash
python cold.py war --domain negotiation --arena career --stakes high --analyze-patterns
```
→ Logs Event ID: `event1`

**Day 5:**
```bash
python cold_outcome.py event1 --mode war
# Outcome: partial, damage 0.4, benefit 0.8
```
→ Pattern detected: escalation sometimes works, sometimes doesn't

**Day 15:**
```bash
python cold.py war --domain negotiation --arena career --stakes high --analyze-patterns
```
→ Now N is more cautious (learned from event1 outcome)
→ Logs Event ID: `event2`

**Day 25:**
```bash
python cold_outcome.py event2 --mode war
# Outcome: success, damage 0.1, benefit 0.95
```
→ Pattern strengthens: caution works better

**Day 40:**
```bash
python cold.py war --domain negotiation --arena career --stakes high --analyze-patterns
```
→ N is even MORE cautious (two successes with caution, one mixed outcome with escalation)

---

## Memory Storage

All decisions and outcomes are stored in:

```
data/memory/cold_strategist.db
```

This is an SQLite database with tables:
- `events`: All decisions analyzed
- `outcomes`: How decisions turned out
- `patterns`: Recurring behaviors detected
- `calibrations`: N's current adjustment factors
- `overrides`: When you ignored counsel
- `ministers_called`: Who participated in each decision

You can inspect it:

```bash
sqlite3 data/memory/cold_strategist.db
sqlite> SELECT COUNT(*) FROM events;
sqlite> SELECT pattern_name, frequency FROM patterns;
sqlite> .exit
```

---

## Understanding N's Posture

After pattern analysis, N's posture adjusts in three ways:

### 1. Caution (war_caution)
- Default: 1.0 (baseline)
- Adjusted Down: 0.70 (more cautious)
- Meaning: If you've escalated before with poor outcomes, N will push back harder on escalation next time

### 2. Urgency Threshold (war_urgency_threshold)
- Default: 1.0 (baseline)
- Adjusted Up: 1.50 (higher threshold)
- Meaning: If you've made rushed decisions with urgency pressure, N will require more evidence before believing something is truly urgent

### 3. Bluntness (war_bluntness)
- Default: 1.0 (baseline)
- Adjusted Up: 1.30 (more blunt)
- Meaning: If you repeatedly ignore counsel, N will be more direct/harsh

---

## Tips

1. **Always save the Event ID** when you log a decision. You'll need it to resolve the outcome.

2. **Log outcomes promptly** once you know the result. Pattern detection is most useful with complete data.

3. **Use `--analyze-patterns`** once you have 5+ decisions in memory. Before that, not enough data for meaningful patterns.

4. **War mode is abstract**. It's safe for:
   - Fiction/games
   - Negotiations you're in
   - Career strategy
   - Self-conflict resolution
   - Any scenario where you want adversarial analysis

5. **N learns over time**. The more decisions you log with outcomes, the better N's calibration becomes.

6. **Check patterns periodically**:
   ```bash
   python -c "
   from core.memory.memory_store import MemoryStore
   from core.memory.pattern_engine import PatternEngine
   
   store = MemoryStore()
   events = store.load_events()
   engine = PatternEngine()
   patterns = engine.detect_patterns(events)
   
   for p in patterns:
       print(f'{p.pattern_name}: freq {p.frequency}, outcome {p.last_outcome}')
   "
   ```

---

## Troubleshooting

**"Event ID: None after decision"**
- You ran with `--log-memory` disabled or there was an error saving
- Check that `data/memory/cold_strategist.db` exists and is writable

**"No patterns detected yet"**
- You need at least 2-3 events with resolved outcomes
- Make sure you've called `cold_outcome.py` to log the results

**"ModuleNotFoundError: No module named 'cli'"**
- Make sure you're running from the `cold_strategist` root directory
- Check that `cli/__init__.py` exists

**"AttributeError: 'WarEngine' has no attribute 'run'"**
- Make sure `core/war/war_engine.py` is up to date
- Check imports in `core/orchestrator/router.py`

---

## Next Steps

1. Try Example 1 (war mode negotiation)
2. Save the Event ID somewhere
3. After the negotiation plays out, run `cold_outcome.py` with that ID
4. Repeat for multiple decisions
5. Once you have 5+ decisions with outcomes, use `--analyze-patterns` to see N's learning
6. Watch N's posture adjust over time

Happy strategizing! 🎯
