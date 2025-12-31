"""
War Mode Minister Selection Bias

Defines which ministers speak in War Mode, how many, and in what order.
No doctrine changes—pure selection reshaping.

Design Principles:
- Prefer leverage-heavy ministers (Power, Psychology, Conflict, Intelligence)
- Limit moral/soft voices (Diplomacy, Discipline) to tactical use only
- Preserve Truth and Risk as guardrails (never veto, always heard)
- Keep debates sharp, bounded, outcome-driven
- Minister-domain relevance determines conditional inclusion
"""

WAR_MINISTER_BIAS = {
    # Ministers always in War Mode council (leverage + guardrails)
    "preferred": [
        "Power",           # Structural pressure, leverage
        "Psychology",      # Messaging, manipulation, morale
        "Conflict",        # Escalation, tactical response
        "Intelligence",    # Information advantage, reconnaissance
        "Narrative",       # Framing, information operations
        "Timing",          # Momentum, tempo advantage
        "Optionality",     # Flexibility, exit strategies
        "Truth",           # Guardrail (always included via hard_rules)
        "Risk & Survival", # Guardrail (always included via hard_rules)
    ],

    # Ministers included if domain-relevant (tactical use)
    "conditional": [
        "Legitimacy",      # Used for cover, international legitimacy
        "Technology",      # Used if digital/tech leverage applies
        "Data",            # Used if metrics, forecasts, or analytics matter
        "Operations",      # Used for execution feasibility
    ],

    # Ministers deprioritized (only if domain forces inclusion)
    "deprioritized": [
        "Diplomacy",       # Only if alliances/negotiations critical
        "Discipline",      # Only if sustained campaigns required
        "Adaptation",      # Only if environment shifts rapidly
    ],

    # Hard rules (never negotiable)
    "hard_rules": {
        "truth_always_included": True,      # Truth never filtered/excluded
        "risk_always_included": True,       # Risk always heard (not as veto, but as guardrail)
        "max_ministers": 5,                 # War Mode talks are fast, bounded
        "min_ministers": 3,                 # Enough diversity to catch blind spots
    },
}
