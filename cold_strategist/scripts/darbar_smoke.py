from cold_strategist.core.darbar import run_full_darbar, SILENCE_STRING
from cold_strategist.core.gatekeeper import Gatekeeper

# Build minimal frozen context
context = {
    "identity": {"domain": "business"},
    "confidence_map": {"overall_context_confidence": 0.8, "unstable_fields": []}
}

decision_question = "Should we accept the partnership?"

# Precomputed positions: all support to trigger PROCEED
ministers = {
    "risk": {
        "minister": "risk",
        "stance": "CONDITIONAL",
        "confidence": 0.9,
        "core_claim": "Downside manageable with loss cap",
        "blocking_conditions": [],
        "non_negotiables": ["hard_loss_cap_percent"],
    },
    "truth": {
        "minister": "truth",
        "stance": "SUPPORT",
        "confidence": 0.85,
        "core_claim": "Evidence supports move",
        "blocking_conditions": [],
        "non_negotiables": [],
    },
    "power": {
        "minister": "power",
        "stance": "CONDITIONAL",
        "confidence": 0.8,
        "core_claim": "Power position improves",
        "blocking_conditions": [],
        "non_negotiables": [],
    }
}

# No objections
ministers_phase2 = None

# Gatekeeper with exhausted budget
g = Gatekeeper('DEC-TEST')
g.max_questions = 0

out = run_full_darbar('DEC-TEST', context, ministers, decision_question, ministers_phase2, gatekeeper=g)
print('DARBAR OUT:', out)
