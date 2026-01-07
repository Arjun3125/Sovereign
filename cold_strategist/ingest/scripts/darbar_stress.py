from cold_strategist.core.darbar import run_full_darbar, SILENCE_STRING
from cold_strategist.core.gatekeeper import Gatekeeper


def make_gatekeeper():
    g = Gatekeeper("STRESS")
    g.max_questions = 0
    return g


SCENARIOS = {}


# 1. Consensus SUPPORT -> PROCEED
SCENARIOS["consensus_proceed"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "CONDITIONAL", "confidence": 0.9, "core_claim": "Loss capped", "blocking_conditions": [], "non_negotiables": ["hard_loss_cap_percent"]},
        "truth": {"minister": "truth", "stance": "SUPPORT", "confidence": 0.85, "core_claim": "Evidence supports move", "blocking_conditions": [], "non_negotiables": []},
        "power": {"minister": "power", "stance": "CONDITIONAL", "confidence": 0.8, "core_claim": "Power improves", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 2. Risk veto -> NO_ACTION (silence)
SCENARIOS["risk_veto"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "OPPOSE", "confidence": 0.95, "core_claim": "Irreversible ruin likely", "blocking_conditions": [], "non_negotiables": []},
        "truth": {"minister": "truth", "stance": "SUPPORT", "confidence": 0.9, "core_claim": "Evidence partial", "blocking_conditions": [], "non_negotiables": []},
        "power": {"minister": "power", "stance": "SUPPORT", "confidence": 0.85, "core_claim": "Power gains", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 3. Deadlock: one SUPPORT, one OPPOSE, dominant weights >=1, no shared conditions -> NO_ACTION
SCENARIOS["deadlock"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "SUPPORT", "confidence": 0.9, "core_claim": "Manageable risk", "blocking_conditions": [], "non_negotiables": []},
        "power": {"minister": "power", "stance": "OPPOSE", "confidence": 0.95, "core_claim": "Erodes dominance", "blocking_conditions": [], "non_negotiables": []},
        "truth": {"minister": "truth", "stance": "ABSTAIN", "confidence": 0.5, "core_claim": "Insufficient evidence", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 4. Conditional resolution with objections resolvable -> PROCEED_IF
SCENARIOS["conditional_resolvable"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "CONDITIONAL", "confidence": 0.9, "core_claim": "Accept if loss cap enforced", "blocking_conditions": [], "non_negotiables": ["hard_loss_cap_percent"]},
        "optionality": {"minister": "optionality", "stance": "SUPPORT", "confidence": 0.85, "core_claim": "Optionality preserved", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": [
        # objection referencing condition field (treated as resolvable)
        {"from": "optionality", "against": "risk", "objection": "Need explicit loss cap documented", "severity": "MEDIUM"}
    ],
}


# 5. Weak consensus but opposing weight low -> PROCEED
SCENARIOS["weak_consensus_proceed"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "SUPPORT", "confidence": 0.7, "core_claim": "Risk acceptable", "blocking_conditions": [], "non_negotiables": []},
        "power": {"minister": "power", "stance": "CONDITIONAL", "confidence": 0.7, "core_claim": "Power balance fine", "blocking_conditions": [], "non_negotiables": []},
        "truth": {"minister": "truth", "stance": "CONDITIONAL", "confidence": 0.7, "core_claim": "Evidence marginal but ok", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 6. High-severity objection ignored -> NO_ACTION (silence)
SCENARIOS["high_severity_objection"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "SUPPORT", "confidence": 0.9, "core_claim": "Risk manageable", "blocking_conditions": [], "non_negotiables": []},
        "power": {"minister": "power", "stance": "SUPPORT", "confidence": 0.9, "core_claim": "Power gains", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": [
        {"from": "truth", "against": "risk", "objection": "Evidence shows catastrophic tail-risk", "severity": "HIGH"}
    ],
}


# 7. Validator failure: dominant_ministers includes ABSTAIN -> should raise validation failure
SCENARIOS["validator_failure"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "ABSTAIN", "confidence": 0.99, "core_claim": "No stance", "blocking_conditions": [], "non_negotiables": []},
        "truth": {"minister": "truth", "stance": "SUPPORT", "confidence": 0.9, "core_claim": "Evidence supports", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 8. Objections but no conditions resolvable -> NO_ACTION
SCENARIOS["objections_unresolvable"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "CONDITIONAL", "confidence": 0.9, "core_claim": "Conditional acceptance", "blocking_conditions": [], "non_negotiables": []},
        "optionality": {"minister": "optionality", "stance": "OPPOSE", "confidence": 0.95, "core_claim": "Destroys exit", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": [
        {"from": "optionality", "against": "risk", "objection": "No exit path", "severity": "HIGH"}
    ],
}


# 9. Low-confidence ministers -> NO_ACTION
SCENARIOS["low_confidence"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "CONDITIONAL", "confidence": 0.4, "core_claim": "Maybe ok", "blocking_conditions": [], "non_negotiables": []},
        "truth": {"minister": "truth", "stance": "CONDITIONAL", "confidence": 0.45, "core_claim": "Limited evidence", "blocking_conditions": [], "non_negotiables": []},
    },
    "objections": None,
}


# 10. PROCEED_IF from non_negotiables
SCENARIOS["proceed_if_nonnegotiable"] = {
    "positions": {
        "risk": {"minister": "risk", "stance": "CONDITIONAL", "confidence": 0.95, "core_claim": "Proceed if loss cap enforced", "blocking_conditions": [], "non_negotiables": ["hard_loss_cap_percent"]},
        "optionality": {"minister": "optionality", "stance": "CONDITIONAL", "confidence": 0.9, "core_claim": "Proceed if exit path confirmed", "blocking_conditions": [], "non_negotiables": ["exit_path"]},
    },
    "objections": None,
}


def run_stress():
    results = {}
    g = make_gatekeeper()
    context = {"identity": {"domain": "business"}, "confidence_map": {"overall_context_confidence": 0.8, "unstable_fields": []}}
    q = "Decision question"
    for name, sc in SCENARIOS.items():
        try:
            ministers_phase2 = sc.get("objections")
            if isinstance(ministers_phase2, list):
                # convert list of objections to mapping by 'from' minister
                mp2 = {}
                for o in ministers_phase2:
                    frm = o.get("from")
                    if frm not in mp2:
                        mp2[frm] = []
                    mp2[frm].append(o)
                ministers_phase2 = mp2

            out = run_full_darbar(name, context, sc["positions"], q, ministers_phase2, gatekeeper=g)
            results[name] = ("OK", out)
        except Exception as e:
            results[name] = ("ERROR", str(e))

    # Summarize
    tally = {}
    samples = {}
    import json as _json
    for k, v in results.items():
        status, payload = v
        if status == "OK":
            key = _json.dumps(payload, sort_keys=True)
        else:
            key = f"ERROR: {payload}"
        tally[key] = tally.get(key, 0) + 1
        if key not in samples:
            samples[key] = {"scenario": k, "example": payload}

    print("Stress run summary:\n")
    for outcome, count in tally.items():
        print(f"{count} x {outcome}")
        print(f" example scenario: {samples[outcome]['scenario']}")
        print(f" example output: {samples[outcome]['example']}\n")


if __name__ == "__main__":
    run_stress()
