"""
WAR MODE INTEGRATION - COMPLETE

Phase 1 War Mode is now fully integrated into Cold Strategist architecture.

✅ COMPLETED

1. core/orchestrator/war_mode.py
   - WarModeEngine: posture filter + constraint enforcer + logger
   - WarContext: goal, domain, reversibility, urgency, emotional_load
   - WarAssessment: feasibility, leverage_map, constraints_hit, cost_profile, recommended_posture
   - Mandatory logging with audit trail

2. core/orchestrator/router.py
   - Imports WarModeEngine and WarContext
   - Singleton _war_engine instance (persists across calls)
   - route("war") returns _handle_war_mode handler
   - _handle_war_mode() builds WarContext from CLI args, evaluates, logs, returns result
   - route_calibration("war") exports logs and audit trail

3. cli/args.py
   - Added --reversibility flag (reversible | partially_reversible | irreversible)
   - Updated validation to require --reversibility for war mode
   - War mode requires: --arena, --reversibility

4. cli/prompts.py
   - Updated Context class to accept reversibility parameter
   - Updated collect_context() to pass reversibility from CLI args

5. scripts/test_war_mode.py
   - Smoke test verifying War Mode evaluation, logging, constraint checking
   - Tests legal goal (negotiation) and illegal goal (blackmail/defame)
   - All tests PASS ✓


✅ FLOW (War Mode Phase 1)

User: cold war --domain negotiation --reversibility reversible --urgency 0.8
     ↓
cli/args.py: parse_args()
  → mode="war", domain="negotiation", reversibility="reversible", urgency=0.8
     ↓
cli/prompts.py: collect_context(args)
  → Context(goal=user_input, domain="negotiation", reversibility="reversible")
  → State(urgency=0.8, emotional_load=args.emotional_load, ...)
     ↓
core/orchestrator/engine.py: run_analysis(mode="war", context, state)
  → Calls route("war")
  → Gets _handle_war_mode handler
     ↓
core/orchestrator/router.py: _handle_war_mode(context, state)
  → Build WarContext(goal, domain, reversibility, urgency, emotional_load)
  → _war_engine.evaluate(war_ctx)
    • Checks hard constraints (legality, individual targeting)
    • If blocked → return "blocked" with stop_reason
    • If viable → derive_leverage(), estimate_cost(), decide_posture()
  → _war_engine.log(assessment, notes=...)
  → Return {mode, assessment, status, recommendation, constraints_hit, cost_profile, leverage_map}
     ↓
N (darbar/n.py): frame_verdict()
  → Display recommendation, cost profile, leverage, constraints
  → Show audit trail
     ↓
User sees: War Mode assessment with full traceability


✅ WHAT DOES NOT HAPPEN YET (Correct)

- Ministers NOT summoned automatically
- RAG NOT queried (no knowledge retrieval in Phase 1)
- No debate layer invoked
- No LLM synthesis

This is intentional. Phase 1 War Mode is:
  ✓ Posture shift (suppress soft biases)
  ✓ Constraint enforcement (block illegal/harmful)
  ✓ Leverage derivation (what moves are available)
  ✓ Cost estimation (reputational, emotional, reversibility)
  ✓ Posture recommendation (withdraw, slow_down, apply_pressure, halt)
  ✓ Audit trail (full logging of suppressions and decisions)

Phase 2 (future):
  - Wire ministers into War Mode
  - Add RAG retrieval (include counter-evidence)
  - Integrate with knowledge synthesis
  - Enable War Mode debate with asymmetric minister selection


✅ TESTING

All modules import successfully:
  ✓ core.orchestrator.war_mode
  ✓ core.orchestrator.router (with War Mode handler)
  ✓ cli.args (with reversibility)
  ✓ cli.prompts (with reversibility support)

War Mode smoke test PASSED:
  ✓ Legal goal (negotiation): feasibility="viable", posture="apply_pressure_structurally"
  ✓ Illegal goal (blackmail): feasibility="blocked", stop_reason="Constraint violation"
  ✓ Leverage derived: tempo_advantage, decision_clarity, fast_iteration
  ✓ Cost profile estimated: reputational, emotional, reversibility, time_cost
  ✓ Logging working: audit trail generated with suppressed biases and risks


✅ SAFETY GUARDRAILS IN PLACE

Hard constraints (NEVER suppressed):
  ✓ legality: Detects forbidden keywords (kill, steal, fraud, blackmail, defame, etc.)
  ✓ individual_harm: Blocks targeting specific people for harm
  ✓ truthfulness: Enforced (future phase will require sources)

Soft constraints (suppressed in War Mode):
  ✓ comfort_bias: Suppressed (show uncomfortable truths)
  ✓ moral_veto: Suppressed (don't filter for "unethical")
  ✓ appeasement_bias: Suppressed (don't default to harmony)

When constraints are violated:
  → assessment.feasibility = "blocked"
  → assessment.stop_reason = "Constraint violation: [list]"
  → Logged for audit trail
  → Posture set to "halt"


✅ AUDIT TRAIL EXAMPLE

[2025-12-27T18:54:16] APPLY_PRESSURE_STRUCTURALLY
  Suppressed biases: comfort_bias, appeasement_bias, moral_veto
  Risks: reputational=medium, emotional=manageable, reversibility=reversible, time_cost=low
  Notes: smoke_test

This log can be retrieved:
  - router.route_calibration("war")["summary"]()
  - _war_engine.get_audit_trail()
  - _war_engine.export_logs()

And later reviewed by N:
  "You chose force posture here. Here's what was suppressed, and here's what it cost."


✅ NEXT STEPS (Phase 2)

1. Wire ministers into War Mode decision
   - Select asymmetric ministers (power, conflict, strategy, diplomacy)
   - Retrieve knowledge with include_counter=True
   - Synthesize advice with lower confidence_threshold
   - Filter with WarModeFilter

2. Integrate War Mode with Darbar debate
   - Use same debate engine, different minister selection + filtering
   - Show suppressed advice alongside approved advice
   - Tribunal judges conflicts in context of War Mode posture

3. Add outcome tracking
   - Log War Mode session ID to memory
   - Later, when outcome is resolved, analyze:
     - Did War Mode advice work?
     - What was the actual cost?
     - Should future War Mode be more/less aggressive?

4. Enable N's post-review
   - User can inspect any War Mode session
   - See what biases were suppressed
   - See what advice was rejected (and why)
   - Understand the cost profile
"""
