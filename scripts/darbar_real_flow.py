import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from cold_strategist.core.darbar import run_full_darbar, SILENCE_STRING
from cold_strategist.core.gatekeeper import Gatekeeper

# Decision statement assembled from user input (declarative, non-emotional)
decision_statement = (
    "Situation: A trusted partner violated an agreement by acting independently with a competitor. "
    "Constraints: No public escalation; long-term relationship value > short-term punishment; power asymmetry favors them slightly. "
    "Objective: Preserve leverage without revealing awareness immediately. "
    "Time horizon: 30-90 days."
)

# Context state must satisfy preconditions
context_state = {
    "confidence_map": {"overall_context_confidence": 0.8, "unstable_fields": []}
}

# Ministers Phase-1 positions matching your provided statements
ministers_phase1 = {
    "power": {
        "minister": "power",
        "stance": "CONDITIONAL",
        "confidence": 0.71,
        "core_claim": "Immediate confrontation destroys leverage; preserve concealment and quietly increase dependency.",
        "blocking_conditions": [],
        "non_negotiables": ["no_public_exposure"]
    },
    "optionality": {
        "minister": "optionality",
        "stance": "CONDITIONAL",
        "confidence": 0.66,
        "core_claim": "Current optionality is low; create two non-obvious exits before signaling.",
        "blocking_conditions": [],
        "non_negotiables": ["preserve_exits"]
    },
    "risk": {
        "minister": "risk",
        "stance": "OPPOSE",
        "confidence": 0.74,
        "core_claim": "Catastrophic downside exists if trust erosion becomes public; delay until downside capped.",
        "blocking_conditions": [],
        "non_negotiables": ["no_reputational_spill"]
    },
    "timing": {
        "minister": "timing",
        "stance": "CONDITIONAL",
        "confidence": 0.69,
        "core_claim": "Current moment unfavorable; optimal window after dependency increase or external distraction (4-8 weeks).",
        "blocking_conditions": [],
        "non_negotiables": []
    }
}

# Gatekeeper (budget frozen)
g = Gatekeeper("real-run")
g.max_questions = 0

result = run_full_darbar("DARBAR-REAL-1", context_state, ministers_phase1, decision_statement, ministers_phase2=None, gatekeeper=g)

print("DARBAR OUTPUT:\n")
if result == SILENCE_STRING:
    print("No action is advised at this time.\nSilence preserves advantage.")
else:
    import json
    print(json.dumps(result, indent=2))
