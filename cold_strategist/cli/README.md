# CLI - Command-Line Interface for Cold Strategist

Entry point for Sovereign Counsel Engine. Provides both **normal** and **war** mode analysis.

## Structure

```
cli/
├── __init__.py       # Module marker
├── args.py           # Argument parsing (flags, validation)
├── prompts.py        # User input collection (Context, State)
├── render.py         # Output formatting (verdicts, patterns, calibration)
└── main.py           # Entry point and main logic
```

## Usage

### Normal Mode (Standard Counsel)

```bash
python cold.py normal --domain career --stakes high
```

**Options:**
- `--domain` (required): `career`, `negotiation`, `self`, `fictional`, `other`
- `--stakes`: `low`, `medium` (default), `high`, `existential`
- `--emotional-load`: 0.0-1.0 (default: 0.3)
- `--urgency`: 0.0-1.0 (default: 0.3)
- `--fatigue`: 0.0-1.0 (default: 0.3)
- `--log-memory`: Enable memory logging (default: enabled)
- `--analyze-patterns`: Analyze recurring patterns (default: disabled)

### War Mode (Adversarial Analysis)

```bash
python cold.py war --domain negotiation --arena career --stakes medium
```

**Options:**
- `--domain` (required): Domain of decision
- `--arena` (required): `career`, `negotiation`, `self-discipline`, `fictional`
- `--stakes`: `low`, `medium` (default), `high`, `existential`
- `--constraints`: Space-separated constraints, e.g., `reversible minimal_collateral legal`
- `--emotional-load`, `--urgency`, `--fatigue`: As above
- `--log-memory`: Log event to SQLite (default: enabled)
- `--analyze-patterns`: Detect war patterns and adjust N's posture (default: disabled)

## Examples

### War Mode Negotiation

```bash
python cold.py war \
  --domain negotiation \
  --arena career \
  --stakes high \
  --constraints reversible minimal_collateral legal \
  --urgency 0.7 \
  --analyze-patterns
```

When prompted:
```
Describe the situation:
> Counterparty is demanding unfavorable terms with 48-hour deadline
```

**Output:**
1. **War Verdict**: Primary move, risk score, reversibility, optionality, alternatives
2. **Event Logged**: Event ID for later outcome resolution
3. **Patterns** (if `--analyze-patterns`): Recurring escalation or override patterns
4. **N's Posture** (if patterns detected): Adjusted caution, urgency threshold, bluntness

### Resolve Outcome (Later)

After the decision plays out:

```bash
python cold_outcome.py <event-id> --mode war
```

When prompted:
```
Outcome result (success | partial | failure):
> failure

Actual damage incurred (0.0-1.0):
> 0.72

Benefit gained (0.0-1.0):
> 0.1

Lessons learned (comma-separated):
> Escalation created unintended hostility, Exit route became blocked
```

**Output:**
- Outcome logged to SQLite
- Memory recalibrated
- Pattern detection re-run
- N's bias adjusted for next similar decision

## Architecture

### Flow

```
CLI Args
  ↓
Prompts (Context, State)
  ↓
Orchestrator Router
  ↓
WarEngine (or normal mode)
  ↓
Event Logged (SQLite)
  ↓
Verdict Rendered
  ↓
(Later) Outcome Logged
  ↓
Pattern Detection
  ↓
N Bias Adjustment
```

### Key Modules

- **`args.py`**: Validates all command-line flags; required params per mode
- **`prompts.py`**: Collects situation description; builds Context/State objects
- **`render.py`**: Formats verdicts, patterns, calibrations for terminal display
- **`main.py`**: Orchestrates the entire flow; calls router, analysis, rendering

### Integration Points

- **CLI → Orchestrator**: `from core.orchestrator.engine import run_analysis`
- **Router**: `from core.orchestrator.router import route, route_calibration`
- **War Mode**: `from core.war import WarEngine`
- **Memory Logging**: `from core.memory.memory_store import MemoryStore`
- **Pattern Detection**: `from core.memory.pattern_engine import PatternEngine`
- **Calibration**: `from core.war.war_calibration import calibrate_n_from_war_patterns`

## Testing

Run the CLI integration test:

```bash
python tests/test_cli_integration.py
```

This validates:
1. Argument parsing (war mode, normal mode, validation)
2. Context/state collection
3. Analysis execution
4. Verdict rendering
5. Pattern detection
6. Learning summary

## Output Examples

### War Verdict

```
======================================================================
VERDICT
======================================================================

PROCEED WITH CAUTION

Primary Move:
  Request extended negotiation window; present counter-proposal with
  escalation clause and face-saving exit for counterparty

Posture: conditional

Risk: ▓▓▓▓▓░░░░░ 45.0%

Reversible: Yes
Optionality: preserved

Alternatives:
  1. Accept terms and cut losses immediately
  2. Walk away and seek alternative partnership

DO NOT:
  ✗ Accept artificial deadline pressure
  ✗ Agree to one-sided clauses without legal review
  ✗ Escalate emotionally

Next Step:
  Schedule call within 12 hours to propose extended timeline

------================================================================
Event ID (save for outcome resolution): a3f7c2e1-9b4d-4a2c-8f1d-2b5e...
----------------------------------------------------------------------
```

### Pattern Detection

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
```

### N's Adjusted Posture

```
======================================================================
N'S ADJUSTED POSTURE
======================================================================

Posture: heightened caution on escalation; skepticism toward urgency claims

Caution: ⬆ 0.70x
Urgency Threshold: ⬆ 1.50x
Bluntness: → 1.00x
```

## Error Handling

- **Missing required args**: Parser shows help and exits
- **Invalid mode/domain**: Validation catches and explains
- **Analysis failure**: Error logged; suggests debugging steps
- **Keyboard interrupt**: Graceful cancel (Ctrl+C)

## Future Extensions

- [ ] LLM-based context inference (enhance user input)
- [ ] Interactive follow-up questions
- [ ] Export verdicts to JSON/Markdown
- [ ] Integration with external decision-tracking tools
- [ ] Batch mode for multiple decisions
