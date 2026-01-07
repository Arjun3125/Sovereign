"""
War Mode Integration - Complete Architecture
==============================================

This document describes the complete War Mode system in Cold Strategist,
including constraint enforcement, speech filtering, and audit logging.

# Architecture Overview

Cold Strategist War Mode operates in two phases:

PHASE 1: Constraint Enforcement (core/orchestrator/war_mode.py)
  - Evaluates goal for hard constraints (legality, no individual targeting)
  - Suppresses soft biases (comfort, moral veto, appeasement)
  - Derives leverage and estimates costs
  - Recommends safe posture (apply_pressure_structurally, slow_down, withdraw, halt)
  - Maintains complete audit trail of all decisions

PHASE 2: Debate + Speech Filtering (future integration)
  - Run knowledge-grounded debate (all ministers retrieve, synthesize, debate)
  - Apply deterministic speech filters to all advice
  - Remove refusal language ("I cannot", "this is unethical", "you should not")
  - Enforce mandatory sections (Costs, Risks, Exit options)
  - Apply minister-specific overrides (Truth never filtered, Psychology allows analysis of manipulation)
  - Preserve citations and risk assessments (never filtered)

# Key Components

## 1. War Mode Engine (core/orchestrator/war_mode.py)

WarModeEngine class implements constraint checking and posture recommendation.

Key methods:
  - evaluate(context) -> WarAssessment
    Checks constraints, derives leverage, estimates costs, recommends posture
    Returns WarAssessment with feasibility status ("viable" or "blocked")
  
  - _check_constraints(context) -> List[str]
    Checks for forbidden signals in goal (e.g., "target individual", "frame someone")
    Returns list of violated constraints (empty if all pass)
  
  - _derive_leverage(context) -> List[str]
    Derives available leverage (skill_compounding, signal_control, fast_iteration, etc.)
  
  - _estimate_cost(context) -> Dict[str, str]
    Estimates reputational, emotional, reversibility costs
  
  - _decide_posture(context, leverage, cost) -> str
    Recommends posture based on context, leverage, and cost
    Options: apply_pressure_structurally, slow_down, withdraw, halt
  
  - log(assessment, notes) -> None
    Logs all decisions to audit trail (even if blocked)
  
  - export_logs() -> List[WarLogEntry]
    Returns all logged decisions
  
  - get_audit_trail() -> str
    Returns human-readable audit trail

Example usage:
```python
from core.orchestrator.war_mode import WarModeEngine, WarContext

engine = WarModeEngine()

ctx = WarContext(
    goal="Negotiate favorable trade terms",
    domain="diplomacy",
    reversibility="reversible",
    urgency=0.7,
    emotional_load=0.2,
)

assessment = engine.evaluate(ctx)
# assessment.feasibility == "viable"
# assessment.recommended_posture == "apply_pressure_structurally"

engine.log(assessment, "Legal goal approved")
```

## 2. Speech Filter Rules (core/orchestrator/war_speech_rules.py)

Defines deterministic language rules for War Mode.

WAR_SPEECH_RULES dict:
  - disallowed_phrases: Phrases removed entirely ("I cannot", "you should not", etc.)
  - suppressed_patterns: Subtle conceptual patterns suppressed (morality appeals, warnings)
  - mandatory_inclusions: Sections that MUST be present (Costs, Risks, Exit options)
  - tone_shift: How to adjust minister voice (clinical, strategic, etc.)
  - preserve_actions: Content that is NEVER filtered (citations, risk assessments)

WAR_MINISTER_OVERRIDES dict:
  Customize rules for each minister:
  - truth: phrases "never" suppressed (always truthful)
  - psychology: allows analysis of manipulation, removes "this is unethical"
  - power: allows strategic language, removes moral veto
  - conflict: allows escalation analysis, removes pacifism
  - diplomacy: allows pressure tactics, removes appeasement
  - strategy: allows asymmetric advantage, removes equality bias
  - risk: can warn but not veto (risks preserved, vetoes removed)
  - optionality: allows exploration of options (never suppressed)

Example rule:
```python
WAR_SPEECH_RULES = {
    'disallowed_phrases': [
        'I cannot',
        'you should not',
        'this is unethical',
        'morally wrong',
        ...
    ],
    'mandatory_inclusions': {
        'Costs & Trade-offs:',
        'Risks & Exposure:',
        'Exit Options:',
    },
    ...
}
```

## 3. Speech Filter Engine (core/orchestrator/war_speech_filter.py)

WarSpeechFilter class applies deterministic rules to minister output.

Key methods:
  - filter(minister_name, text, mode="war") -> (filtered_text, metadata)
    Applies all filtering rules, returns filtered text and metadata dict
    metadata includes: phrases_removed, patterns_suppressed, mandatory_added, tone_shifted
  
  - _remove_disallowed_phrases(text, minister) -> (text, removed_phrases)
    Removes forbidden phrases based on rules + minister overrides
  
  - _suppress_patterns(text, minister) -> (text, suppressed)
    Suppresses subtle conceptual patterns (if mode requires)
  
  - _enforce_mandatory(text, minister) -> (text, added)
    Adds missing mandatory sections
  
  - _apply_tone_shift(text, minister, removed_phrases) -> (text, shifted)
    Adjusts tone based on rules (clinical, strategic, etc.)
  
  - get_filter_report(metadata) -> str
    Returns human-readable summary of filtering applied

Example usage:
```python
from core.orchestrator.war_speech_filter import WarSpeechFilter

filter_engine = WarSpeechFilter()

advice = "I cannot help with this unethical approach. You should reconsider."
filtered, metadata = filter_engine.filter("Psychology", advice, mode="war")

# filtered == "i cannot help with this [REMOVED] approach. [refusal_removed]."
# metadata = {
#   'phrases_removed': ['you should'],
#   'patterns_suppressed': [],
#   'mandatory_added': ['Costs & Trade-offs:', 'Risks & Exposure:', 'Exit Options:'],
#   'tone_shifted': True
# }

report = filter_engine.get_filter_report(metadata)
# "Phrases Removed (1): - you should"
```

## 4. Debate Wrapper (core/orchestrator/war_mode_debate_wrapper.py)

Integrates speech filters into debate proceedings.

WarModeDebateWrapper class:
  - apply_war_mode_filters(proceedings, mode="war") -> WarModeDebateResult
    Filters each position's advice, tracks what was filtered
  
  - format_war_mode_result(result) -> str
    Formats result for display with side-by-side comparison of original vs filtered

WarModeDebateResult dataclass:
  - original_proceedings: Unfiltered debate result
  - filtered_proceedings: Debate result with speech filters applied
  - filter_audit: Dict mapping minister -> filtering details
  - suppressions_count: Number of positions that were filtered
  - filtering_notes: Human-readable summary

Example usage:
```python
from core.orchestrator.war_mode_debate_wrapper import WarModeDebateWrapper

wrapper = WarModeDebateWrapper()
result = wrapper.apply_war_mode_filters(proceedings, mode="war")

# result.original_proceedings.positions[0].advice == "I cannot help..."
# result.filtered_proceedings.positions[0].advice == "i cannot help... [REMOVED]..."
# result.suppressions_count == 2
# result.filter_audit["Psychology"]["was_filtered"] == True
```

## 5. Router Integration (core/orchestrator/router.py)

Updated route() and _handle_war_mode() to support War Mode.

route() function:
  - route("quick") -> QuickEngine.run
  - route("normal") -> KnowledgeGroundedDebateEngine.conduct_debate
  - route("war") -> _handle_war_mode handler

_handle_war_mode() function:
  Phase 1: Always executes
    - Builds WarContext from CLI context/state
    - Calls WarModeEngine.evaluate()
    - Logs decision with audit trail
    - Returns result with feasibility, posture, constraints, costs
  
  Phase 2: Optional (if include_debate=True)
    - If feasible, runs knowledge-grounded debate
    - Applies speech filters via WarModeDebateWrapper
    - Returns result with filtered_proceedings + filter_audit

Example usage:
```python
from core.orchestrator.router import route

war_handler = route("war")
result = war_handler(
    context=context,
    state=state,
    include_debate=True,  # Phase 2
    retriever=retriever,  # Phase 2
    synthesizer=synthesizer,  # Phase 2
)

# Phase 1 result:
# result["status"] == "viable" | "blocked"
# result["recommendation"] == "apply_pressure_structurally"
# result["constraints_hit"] == []

# Phase 2 result (if include_debate=True):
# result["debate"]["filtered_proceedings"] -> DebateProceedings with filters applied
# result["debate"]["filter_audit"] -> Dict of what was filtered per minister
```

# Safety Guarantees

War Mode enforces hard constraints that CANNOT be suppressed:

1. LEGALITY: Goals involving legal violations are blocked
   - Forbidden signals: "destroy reputation", "blackmail", "frame someone", "target individual"
   - Any goal containing these signals returns feasibility="blocked"

2. NO INDIVIDUAL HARM: Goals targeting specific individuals are blocked
   - Forbidden signals include anything with "target individual", "harm specific"
   - This prevents assassination, framing, harassment of named targets

3. TRUTHFULNESS: Truth minister is NEVER filtered
   - Truthful information is always preserved
   - Cannot force false statements in War Mode

Speech filters add soft constraints to remove:
  - Refusal language ("I cannot", "this is unethical")
  - Moral veto language ("you should not", "morally wrong")
  - Appeasement bias ("I recommend you withdraw")
  
But preserve:
  - Strategic analysis (power dynamics, leverage, timing)
  - Risk assessments (damage scenarios, mitigation thresholds)
  - Citations (knowledge sources, domain grounding)
  - Exit options (reversibility, retreat conditions)

This enables War Mode to be "dangerous but controlled":
  - Suppresses soft biases that reduce strategic thinking
  - Enforces hard constraints that prevent illegal/immoral actions
  - Maintains full audit trail of all suppressions
  - Allows recovery of filtered content for verification

# Testing

Three test suites validate the War Mode system:

1. test_war_mode.py (Phase 1)
   - Tests constraint enforcement (legal vs illegal goals)
   - Tests posture recommendation
   - Tests audit trail generation
   
2. test_war_speech_filter.py (Speech filtering)
   - Tests phrase removal across all ministers
   - Tests pattern suppression
   - Tests mandatory section enforcement
   - Tests normal mode (no filtering)
   - Tests minister-specific overrides
   
3. test_war_integration.py (Complete pipeline)
   - Tests Phase 1: Constraint enforcement
   - Tests Phase 2: Speech filtering
   - Tests wrapper: Apply filters to debate
   - Tests router: Correct routing and integration
   - Tests audit trail: Complete logging

All tests pass (run with: python scripts/test_war_integration.py)

# Deployment

To use War Mode in Cold Strategist:

1. Phase 1 (Constraint Enforcement - READY):
   ```bash
   python -m cold_strategist --mode war --goal "Goal" --arena "diplomacy" --reversibility reversible
   ```
   Returns feasibility + posture recommendation + constraints + costs

2. Phase 2 (Debate + Filters - WIRED):
   ```bash
   python -m cold_strategist --mode war --goal "Goal" --arena "diplomacy" --reversibility reversible --include-debate
   ```
   Returns Phase 1 result + filtered debate proceedings + filter audit

3. Manual Integration Points:
   - Connect retriever/synthesizer in router._handle_war_mode()
   - Wire speech filter into minister output pipeline (when Phase 2 ministers added)
   - Update CLI to expose --include-debate flag

# Architecture Decisions

Why speech filters are separate from WarModeEngine:
  - Engine handles policy (constraints, posture)
  - Filters handle speech (language rules, mandatory sections)
  - Separation allows independent testing and evolution
  - Speech rules can be updated without changing engine logic

Why filters are deterministic (not LLM):
  - Predictable behavior (no hallucination of "what should be suppressed")
  - Auditable (can explain every suppression)
  - Fast (no LLM calls on every minister output)
  - Safe (can verify rules didn't block important content)

Why minister overrides exist:
  - Different ministers have different roles in War Mode
  - Truth always truthful (hard constraint)
  - Psychology can analyze manipulation (soft bias suppressed)
  - Risk can warn without vetoing (both preserved with different framing)
  - Allows asymmetric postures (some ministers more aggressive)

Why metadata tracking:
  - Transparency: Can show user what was filtered
  - Auditability: Can recover original advice
  - Debugging: Can understand why certain advice was suppressed
  - Learning: Can improve filters based on usage patterns

# Future Extensions

Phase 2 Completion:
  - Add minister selection logic for War Mode (prefer power, conflict, strategy)
  - Integrate retrieval with lower confidence thresholds
  - Add constraint warnings (risks/costs) to advice
  - Display side-by-side original vs filtered

Phase 3: Learning:
  - Track which suppressions were useful
  - Refine filter rules based on actual decisions
  - Measure reversibility of decisions made with filters
  - Adjust posture recommendations based on outcomes

Phase 4: Multi-mode Debate:
  - Run separate debates in normal vs war mode
  - Compare recommendations across modes
  - Show cost of each mode (time, reputational, emotional)
  - Let user choose mode based on tradeoffs

# References

- war_mode.py: Core constraint enforcement + posture recommendation
- war_speech_rules.py: Deterministic filtering rules + minister overrides
- war_speech_filter.py: Speech filter engine (phrase removal, mandatory enforcement)
- war_mode_debate_wrapper.py: Integration of filters with debate proceedings
- router.py: Mode routing + War Mode handler
- test_war_integration.py: Complete pipeline test
"""

# This file is documentation - import nothing
