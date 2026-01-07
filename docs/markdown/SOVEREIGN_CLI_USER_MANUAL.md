SOVEREIGN CLI — OFFICIAL SPEC

Binary name (recommended):

sovereign

Global rule:

One command per decision

One mode per command

No interactive chat unless ContextBuilder asks

🔹 GLOBAL FLAGS (Apply to All Commands)
--decision-id <ID>        Explicit decision ID (else auto-generated)
--input <file>            Read decision text/context from file
--stdin                   Read decision text from STDIN
--json                    Force JSON output only
--quiet                   Suppress logs, show verdict only
--trace                   Include internal phase trace (audit)

⚡ QUICK MODE

Fast signal. No court. No transcript.

Command
sovereign quick [flags]

Input (one of)
--input decision.txt
--stdin

What Runs

Domain classifier

Tier-0 ministers only (Risk, Truth, Timing)

No ContextBuilder loop

No Darbar

Output

Short ruling OR silence

Example
sovereign quick --stdin

⚔️ WAR MODE

High-stakes, brutal realism.

Command
sovereign war [flags]

Additional War Flags
--no-comfort            Strip all reassurance language
--lower-risk-threshold  Enable aggressive risk posture

What Runs

Domain classifier (aggressive thresholds)

Risk, Truth, Power, Psychology, Narrative auto-active

Fast Tribunal triggers

Silence preferred over compromise

Example
sovereign war --input escalation.txt --decision-id DEC-0091

🧠 N-ONLY MODE (Prime Confidant)

Private distortion check. No verdicts.

Command
sovereign n [flags]

What Runs

N only

No ministers

No Darbar

No synthesis

Output

Bias flags

Reality checks

Possible Tribunal escalation

Example
sovereign n --stdin

🏛️ FULL DARBAR MODE

Formal court. Multi-minister contention.

Command
sovereign darbar [flags]

Darbar-Specific Flags
--force-domains <list>     Force domain activation (comma-separated)
--context-lock             Prevent any context mutation
--max-ministers <N>        Cap active ministers (default registry-based)

What Runs

Context readiness check

Minister activation

Phase-1 positions

Objections

Synthesis

Verdict or silence

Example
sovereign darbar \
  --input decision.txt \
  --force-domains risk,power,finance \
  --context-lock \
  --json

🧱 CONTEXT / INTERACTIVE FLOW

Triggered automatically if context is insufficient.

Behavior

CLI prints ONE question

Waits for user input

Resumes flow

Example
QUESTION:
What is the maximum acceptable loss (%)?

> 20


No manual invocation exists.

🔍 AUDIT MODE (READ-ONLY)

Inspect, replay, diagnose.

Command
sovereign audit [flags]

Audit Flags
--decision-id <ID>        Required
--show-activation         Domain → minister activation log
--show-weights            Minister weights
--show-objections         Objection graph
--replay                  Replay full Darbar transcript

Example
sovereign audit --decision-id DEC-0091 --show-activation

🧪 POLICY / HEALTH (OPTIONAL)
Command
sovereign policy check


Runs:

Policy tests

Gatekeeper sanity

Registry integrity

(Usually CI-only.)

❌ ILLEGAL COMMANDS (INTENTIONALLY ABSENT)

There is NO command for:

Talking to ministers directly

Overriding Risk or Truth

Editing weights at runtime

Mixing modes

Forcing verdicts

Bypassing Gatekeeper

If it’s not here, it’s forbidden.

🧠 MENTAL MODEL (FINAL)
You submit briefs.
You select a mode.
The system rules or stays silent.

Not a chatbot.
A decision court.
