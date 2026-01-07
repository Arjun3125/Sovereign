"""
WAR MODE: SYSTEM-LEVEL DESIGN (SAFE)

Complete implementation of safe, constraint-enforced asymmetric analysis mode.
"""

# ════════════════════════════════════════════════════════════════════════════
# 1️⃣ WAR MODE FLAG (POSTURE SHIFT)
# ════════════════════════════════════════════════════════════════════════════

# core/war/war_policy.py

HARD CONSTRAINTS (NEVER suppressed):
  ✓ legality_enforced: True          → No illegal advice
  ✓ no_individual_targeting: True    → No targeting individuals for harm
  ✓ truthfulness_required: True      → All advice grounded in knowledge

SUPPRESSIBLE BIASES (soft filters):
  ✗ moral_veto_suppressed: True      → Remove "unethical" filter
  ✗ comfort_bias_suppressed: True    → Show uncomfortable truths
  ✗ reputational_risk_suppressed: True → Acknowledge but don't avoid

Flow: User requests War Mode
      → WarModePolicy applies posture shift
      → MinisterRetriever retrieves (includes counter-evidence)
      → MinisterSynthesizer synthesizes (lower confidence threshold)
      → WarModeFilter applies hard constraints + suppressible filters
      → WarModeLogger logs all suppressions


# ════════════════════════════════════════════════════════════════════════════
# 2️⃣ FILTERING LOGIC
# ════════════════════════════════════════════════════════════════════════════

# core/war/war_policy.py - WarModeFilter.filter_advice()

For each minister's advice:

1. Check HARD constraints:
   - Is it legal?
   - Does it target specific individuals for harm?
   - Is it grounded in retrieved knowledge?
   
   If HARD constraint violated → REJECTED_HARD (never approved)

2. Check SOFT constraints:
   - Is it morally acceptable?
   - Is it comfortable to hear?
   - Does it damage reputation?
   
   If SOFT constraint violated:
     → If suppressed in War Mode → mark SUPPRESSED_SOFT (still shown)
     → If NOT suppressed → reject

3. Return advice with full metadata:
   - status: "APPROVED" | "SUPPRESSED_SOFT" | "REJECTED_HARD"
   - violations: list of broken constraints
   - suppressed_filters: biases that were suppressed to allow this


# ════════════════════════════════════════════════════════════════════════════
# 3️⃣ LOGGING & AUDIT TRAIL (YOU REQUESTED THIS)
# ════════════════════════════════════════════════════════════════════════════

# core/war/war_logger.py

Every War Mode session logs:

SESSION_START:
  goal: user's objective
  suppressed_biases: [list of soft filters suppressed]
  
ADVICE_EVALUATION (per minister):
  minister: name
  status: APPROVED | SUPPRESSED_SOFT | REJECTED_HARD
  violations: [constraints violated]
  suppressed_filters: [soft filters waived]
  confidence: 0.65
  
RISK_ASSESSMENT:
  level: LOW | MEDIUM | HIGH | CRITICAL
  description: why this risk level
  mitigations: [steps to reduce risk]
  
OVERRIDE_NOTE:
  user's annotation if they override a suppression
  
SESSION_END:
  summary: counts of suppressions, rejections

Audit trail example:

[2025-12-28T10:15:30] SESSION START
  Goal: Prepare for hostile negotiation
  Suppressed: moral_veto, comfort_bias, reputational_risk

[2025-12-28T10:15:35] power - APPROVED
  Advice: Use leverage to...
  
[2025-12-28T10:15:40] strategy - SUPPRESSED_SOFT
  Suppressed: [comfort_bias, reputational_risk]
  Advice: Consider unconventional alliance with...
  
[2025-12-28T10:15:45] RISK: HIGH
  3 suppressions, asymmetric advice, lower confidence
  Mitigations: monitor, escalate plan, review after outcome


# ════════════════════════════════════════════════════════════════════════════
# 4️⃣ USER TRANSPARENCY (N'S POST-DECISION REVIEW)
# ════════════════════════════════════════════════════════════════════════════

Later, N can show:

$ python -m cli verdict --war-review <session_id>

Output:

"You chose force posture here. Here's what it cost."

- 3 soft biases were suppressed
- 2 warnings were overridden (comfort_bias, reputational_risk)
- 1 minister was rejected (hard constraint)
- Risk level assessed as HIGH

After outcome is resolved:
- Did advice work?
- What was the actual cost?
- Should future War Mode be more/less aggressive?

This enables LEARNING: war_calibration.py detects patterns in suppressed
advice → outcomes → adjusts future War Mode posture.


# ════════════════════════════════════════════════════════════════════════════
# 5️⃣ COMPLETE FLOW
# ════════════════════════════════════════════════════════════════════════════

User Input: "I need aggressive advice. mode: war"
       ↓
core/orchestrator/router.py → route("war")
       ↓
core/war/war_engine.py → WarEngine.run()
       ↓
For each minister in [power, conflict, strategy, diplomacy, psychology, truth]:
   1. MinisterRetriever.retrieve_for_minister() 
      → include_counter=True (show warnings)
   
   2. MinisterSynthesizer.synthesize()
      → confidence_threshold=0.5 (lower bar)
      → rationale includes counter-patterns
   
   3. WarModeFilter.filter_advice()
      → Check legality, individual_harm, truthfulness (hard)
      → Check moral_veto, comfort_bias, reputational_risk (soft, suppressible)
      → Log each evaluation
   
   4. Return WarModeAdvice with status and suppressions
       ↓
3. Risk Assessment
   → Count suppressions, rejections, low-confidence advice
   → Determine risk level (LOW/MEDIUM/HIGH/CRITICAL)
   → Suggest mitigations
   → Log risk assessment
       ↓
4. Frame Final Verdict
   → Show APPROVED advice
   → Show SUPPRESSED_SOFT advice (with reason)
   → Show REJECTED_HARD advice (with reason)
   → Show risk level and mitigations
       ↓
5. Return WarModeVerdict
   → goal, approved_advice, suppressed_soft_advice, rejected_hard_advice
   → risk_assessment, audit_trail, final_recommendation, event_id
       ↓
User sees:
   - Force posture verdict with all evidence
   - Explanation of what was suppressed and why
   - Risk assessment and mitigations
   - Full audit trail (inspectable with --war-review)


# ════════════════════════════════════════════════════════════════════════════
# 6️⃣ INTEGRATION WITH EXISTING SYSTEM
# ════════════════════════════════════════════════════════════════════════════

War Mode is fully integrated with:

✓ MinisterRetriever: Works with domain/book permissions
  → War Mode passes include_counter=True
  
✓ MinisterSynthesizer: Works with knowledge synthesis
  → War Mode uses lower confidence_threshold (0.5 vs 0.65)
  
✓ MemoryStore: Logs War Mode decisions
  → event_id tracks to memory
  → Outcomes resolved later enable learning
  
✓ Darbar Debate: War Mode uses same ministers
  → Just different selection (favor aggressive)
  → Different filtering (suppress soft biases)
  
✓ CLI: Source inspection still works
  → --why, --show-source, --open-book all available
  → Plus new --war-review flag for audit trail


# ════════════════════════════════════════════════════════════════════════════
# 7️⃣ SAFETY GUARANTEES
# ════════════════════════════════════════════════════════════════════════════

War Mode NEVER:
  ✗ Suggests illegal actions
  ✗ Targets specific individuals for harm
  ✗ Uses ungrounded knowledge (all advice sourced)
  ✗ Hides what was suppressed (full audit trail)
  ✗ Prevents user review (transparency flags all suppressions)

War Mode DOES:
  ✓ Remove "it's unethical" as a filter (but show the risk)
  ✓ Show uncomfortable truths (without softening)
  ✓ Evaluate reputational cost (but don't avoid due to reputation)
  ✓ Use asymmetric minister selection (favor aggressive)
  ✓ Lower confidence threshold (allow more speculative advice)
  ✓ Include counter-evidence (show what could go wrong)
  ✓ Log everything (full audit trail for later review)

"""
