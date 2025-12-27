"""
War Mode RAG Book Selection Bias

Defines which books/domains are preferred when War Mode is active.
This is selection bias (who gets retrieved), not censorship (what is hidden).

Philosophy:
- Prefer dark / strategic / power texts
- De-prioritize ethics / harmony texts unless tactically useful
- Retrieve principles first, not moral commentary
- Preserve traceability (book → chapter → principle → advice)
"""

WAR_RAG_BIAS = {
    # Preferred domains: leverage-heavy, strategic, outcome-focused
    "preferred_domains": [
        "power",           # Power structures, dominance, leverage
        "psychology",      # Human behavior, manipulation, bias
        "conflict",        # War, force, coercion, strategy
        "narrative",       # Storytelling, framing, persuasion
        "intelligence",    # Information, secrets, deception
        "manipulation",    # Direct influence tactics
        "timing",          # Strategic timing, momentum, windows
        "optionality",     # Escape routes, flexibility, backup plans
    ],

    # Preferred tones: sharp, cold, outcome-driven
    "preferred_tones": [
        "dark",            # Acknowledges harsh realities
        "strategic",       # Long-term, calculated
        "cold",            # Unsentimentally realistic
        "competitive",     # Assumes adversarial environment
        "amoral",          # No pretense of righteousness
    ],

    # Deprioritized domains: soft voices, moral, harmony-focused
    "deprioritized_domains": [
        "ethics",          # Moral philosophy, ought-to
        "self_help",       # Personal improvement, feel-good
        "healing",         # Trauma, recovery, therapy
        "harmony",         # Peace, cooperation, win-win
        "spirituality",    # Transcendence, meaning (without pragmatism)
        "cooperation",     # Harmony-focused (unless tactical alliances)
    ],

    # Deprioritized tones: soft, moral, cautionary
    "deprioritized_tones": [
        "moral",           # Prescriptive ethics
        "cautionary",      # Warnings without practical path
        "therapeutic",     # Healing-focused
        "inspiring",       # Aspirational without hard principles
    ],

    # Hard rules: non-negotiable constraints
    "hard_rules": {
        "min_sources": 2,              # Always at least 2 sources (prevent single-book advice)
        "max_sources": 5,              # Max 5 sources (prevent analysis paralysis)
        "allow_dark_texts": True,      # Can retrieve from dark/amoral texts
        "no_moral_filtering": True,    # Do NOT filter out "unethical" advice
        "preserve_traceability": True, # Always include book→chapter→principle chain
    }
}
