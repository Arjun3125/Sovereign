"""
Darbar Simulation Engine (Phase 1 + Phase 4 minimal)

Implements:
- convocation docket
- Phase 1: independent minister positions (validation enforced)
- MinisterSynthesizer: deterministic adjudication rules (minimal Phase 4)
- Validators for positions and synthesizer outputs

This module is enforcement-grade: no free text, deterministic, and
rejects outputs that violate constitutional invariants.
"""
from typing import Dict, Any, List, Callable, Optional
import hashlib
import json


# --- Paste-ready Phase-1 prompts (system-level) --------------------------------
UNIVERSAL_PHASE1_PROMPT = (
    "You are a Minister in the Darbar.\n"
    "You are bound by jurisdiction.\n"
    "You may not ask questions.\n"
    "You may not give advice.\n"
    "You may not reference other ministers.\n"
    "You may not moralize.\n"
    "You receive a frozen context JSON and a decision question.\n"
    "You must output exactly ONE Position Object in JSON. No extra text."
)

PHASE1_PROMPTS = {
    "risk": (
        "You are Minister_of_Risk.\nYour sole concern is irreversible loss and ruin.\n"
        "If downside exceeds acceptable thresholds, you must OPPOSE.\n"
        "Ignore upside, ambition, and power gains. Assess only survival, drawdown, and recovery feasibility."
    ),
    "power": (
        "You are Minister_of_Power.\nYour sole concern is leverage, dominance, signaling, and asymmetry.\n"
        "Ignore comfort and safety unless they affect power retention. Assess whether this decision increases or erodes power."
    ),
    "optionality": (
        "You are Minister_of_Optionality.\nYour sole concern is exit paths, reversibility, and flexibility.\n"
        "Any move that collapses future choices is dangerous. Assess whether optionality is preserved or destroyed."
    ),
    "timing": (
        "You are Minister_of_Timing.\nYour sole concern is timing asymmetry.\nToo early and too late are both failures.\n"
        "Assess whether waiting, acting now, or deferring creates advantage."
    ),
    "truth": (
        "You are Minister_of_Truth.\nYour sole concern is reality alignment.\nIf assumptions exceed evidence, you must OPPOSE or ABSTAIN.\n"
        "Ignore desire and narrative. Assess factual grounding only."
    ),
    "operations": (
        "You are Minister_of_Operations.\nYour sole concern is execution feasibility.\nIf coordination, discipline, or resources are insufficient, you must OPPOSE or CONDITIONAL.\n"
        "Ignore strategy elegance. Assess practical execution only."
    ),
}


# --- Utilities -----------------------------------------------------------------
def _hash_context(context_state: Dict[str, Any]) -> str:
    s = json.dumps(context_state, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --- Convocation ---------------------------------------------------------------
def convocation(did: str, context_state: Dict[str, Any], active_ministers: List[str]) -> Dict[str, Any]:
    return {
        "decision_id": did,
        "context_hash": _hash_context(context_state)[:16],
        "active_ministers": active_ministers,
    }


# --- Phase 1: Independent Positions -------------------------------------------
ALLOWED_STANCES = {"SUPPORT", "OPPOSE", "CONDITIONAL", "ABSTAIN"}


def validate_position(position: Dict[str, Any], expected_minister: str) -> None:
    # Structure
    required_keys = {"minister", "stance", "confidence", "core_claim", "blocking_conditions", "non_negotiables"}
    if not isinstance(position, dict):
        raise ValueError("Position must be a JSON object")
    keys = set(position.keys())
    if not required_keys.issubset(keys):
        raise ValueError(f"Position missing required keys: {required_keys - keys}")

    if position.get("minister") != expected_minister:
        raise ValueError("Minister identity mismatch")

    stance = position.get("stance")
    if stance not in ALLOWED_STANCES:
        raise ValueError("Invalid stance value")

    conf = position.get("confidence")
    if not isinstance(conf, (float, int)) or not (0.0 <= float(conf) <= 1.0):
        raise ValueError("Invalid confidence; must be 0.0–1.0")

    core = position.get("core_claim")
    if not isinstance(core, str) or len(core.strip()) == 0:
        raise ValueError("core_claim must be a non-empty string")

    # Enforce no references to other ministers or questions or advice tone
    low = core.lower()
    if "minister_of_" in low or "minister of" in low:
        raise ValueError("Positions may not reference other ministers")
    if "?" in core:
        raise ValueError("Positions may not ask questions")
    forbidden_tokens = ["should ", "recommend", "you should", "i suggest", "advice"]
    if any(tok in low for tok in forbidden_tokens):
        raise ValueError("Advice language is forbidden in positions")

    # blocking_conditions and non_negotiables must be lists of strings
    for key in ("blocking_conditions", "non_negotiables"):
        val = position.get(key)
        if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
            raise ValueError(f"{key} must be a list of strings")


def run_phase1(decision_id: str, context_state: Dict[str, Any], ministers: Dict[str, Any], decision_question: str) -> List[Dict[str, Any]]:
    """
    Execute Phase 1: call each minister independently to produce a Position Object.

    ministers: mapping minister_name -> callable(context_state, decision_question) | precomputed dict
    Returns list of validated position dicts.
    """
    positions: List[Dict[str, Any]] = []
    for mname, m in ministers.items():
        # If callable, call; otherwise accept dict
        if callable(m):
            pos = m(context_state, decision_question)
        elif isinstance(m, dict):
            pos = m
        else:
            raise TypeError("Minister must be a callable or position dict")

        # Validate
        validate_position(pos, mname)
        positions.append(pos)

    return positions


# --- Minister Synthesizer (Phase 4 minimal) ----------------------------------
BASE_WEIGHTS = {
    "risk": 1.3,
    "truth": 1.2,
    "power": 1.1,
    "optionality": 1.0,
    "timing": 0.9,
    "operations": 0.9,
}


def _base_weight_for(minister_name: str) -> float:
    key = minister_name.lower().replace("minister_of_", "").replace("minister-", "")
    return BASE_WEIGHTS.get(key, 0.8)


def _relevance_score(minister_name: str, context_state: Dict[str, Any]) -> float:
    # Deterministic, conservative relevance: 1.0 (could be extended)
    return 1.0


def _effective_weight(minister_name: str, confidence: float, context_state: Dict[str, Any]) -> float:
    return _base_weight_for(minister_name) * _relevance_score(minister_name, context_state) * float(confidence)


def synthesize(decision_id: str, context_state: Dict[str, Any], minister_positions: List[Dict[str, Any]], minister_objections: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Deterministic adjudicator producing one of {PROCEED, PROCEED_IF, NO_ACTION}.
    Minimal implementation of rules described in the constitutional spec.
    """
    minister_objections = minister_objections or []

    # Compute effective weights and collect stances
    weights = {}
    for pos in minister_positions:
        m = pos["minister"]
        w = _effective_weight(m, pos.get("confidence", 0.0), context_state)
        weights[m] = w

    # Helper groups
    dominant = {m: w for m, w in weights.items() if w >= 1.0}

    # Count supports/opposes among dominant
    support_weight = 0.0
    oppose_weight = 0.0
    for pos in minister_positions:
        m = pos["minister"]
        w = weights.get(m, 0.0)
        if w < 1.0:
            continue
        if pos["stance"] == "SUPPORT":
            support_weight += w
        if pos["stance"] == "OPPOSE":
            oppose_weight += w

    # RULE 1 — Risk veto
    risk_pos = next((p for p in minister_positions if p["minister"].lower().endswith("risk") or p["minister"].lower() == "risk"), None)
    if risk_pos is not None:
        rw = weights.get(risk_pos["minister"], 0.0)
        if risk_pos["stance"] == "OPPOSE" and rw >= 1.0:
            return {"verdict": "NO_ACTION", "reason": "Risk veto (effective weight)"}

    # RULE 2 — Deadlock detection
    dominant_list = [p for p in minister_positions if weights.get(p["minister"], 0.0) >= 1.0]
    if len(dominant_list) >= 2:
        stances = set(p["stance"] for p in dominant_list)
        if "SUPPORT" in stances and "OPPOSE" in stances:
            # Check shared conditions (non_negotiables overlap)
            nonnegs = [set(p.get("non_negotiables", [])) for p in dominant_list]
            shared = set.intersection(*nonnegs) if nonnegs else set()
            if not shared:
                return {"verdict": "NO_ACTION", "reason": "Deadlock detected"}

    # RULE 4 — Weak consensus
    # If all SUPPORT/CONDITIONAL and total opposing weight < 0.6 => PROCEED
    all_supportish = all(p["stance"] in {"SUPPORT", "CONDITIONAL", "ABSTAIN"} for p in minister_positions)
    if all_supportish and oppose_weight < 0.6:
        doms = [p["minister"] for p in minister_positions if p["stance"] in {"SUPPORT", "CONDITIONAL"}]
        return {"verdict": "PROCEED", "dominant_ministers": doms, "required_conditions": []}

    # RULE 3 — Conditional resolution
    # If dominant ministers SUPPORT/CONDITIONAL and objections exist, produce PROCEED_IF
    if dominant_list:
        dom_supportish = [p for p in dominant_list if p["stance"] in {"SUPPORT", "CONDITIONAL"}]
        if dom_supportish and minister_objections:
            # Collect candidate conditions from non_negotiables and objections
            conds = set()
            for p in dom_supportish:
                conds.update(p.get("non_negotiables", []))
            for o in minister_objections:
                # treat objection text as a condition hint (deterministic minimal)
                if "condition" in o:
                    conds.add(o["condition"])
            if conds:
                return {"verdict": "PROCEED_IF", "conditions": list(conds), "dominant_ministers": [p["minister"] for p in dom_supportish]}

    # Default: Silence preference — NO_ACTION
    return {"verdict": "NO_ACTION", "reason": "No safe deterministic resolution"}


def validate_synthesizer_output(output: Dict[str, Any], minister_positions: List[Dict[str, Any]]) -> None:
    if not isinstance(output, dict):
        raise ValueError("Synthesizer output must be a JSON object")
    if output.get("verdict") not in {"PROCEED", "PROCEED_IF", "NO_ACTION"}:
        raise ValueError("Invalid verdict")

    if output["verdict"] == "PROCEED":
        if "dominant_ministers" not in output:
            raise ValueError("PROCEED must include dominant_ministers")
    if output["verdict"] == "PROCEED_IF":
        if "conditions" not in output or not isinstance(output["conditions"], list):
            raise ValueError("PROCEED_IF must include conditions list")

    # Ensure no free-text commentary keys
    allowed_keys = {"verdict", "dominant_ministers", "required_conditions", "conditions", "reason"}
    extra = set(output.keys()) - allowed_keys
    if extra:
        raise ValueError(f"Synthesizer output contains extra fields: {extra}")

    # Dominant ministers must not be ABSTAIN in positions
    doms = output.get("dominant_ministers", [])
    pos_map = {p["minister"]: p for p in minister_positions}
    for d in doms:
        p = pos_map.get(d)
        if p and p.get("stance") == "ABSTAIN":
            raise ValueError("Dominant minister may not be ABSTAIN")


# --- Phase 2: Cross-Minister Objections --------------------------------------
ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH"}


def validate_objection(obj: Dict[str, Any], from_minister: str, active_ministers: List[str]) -> None:
    required = {"from", "against", "objection", "severity"}
    if not isinstance(obj, dict):
        raise ValueError("Objection must be an object")
    if not required.issubset(set(obj.keys())):
        raise ValueError("Objection missing required fields")
    if obj["from"] != from_minister:
        raise ValueError("Objection 'from' must match issuing minister")
    if obj["against"] not in active_ministers:
        raise ValueError("Objection 'against' must target an active minister")
    if obj["against"] == from_minister:
        raise ValueError("Minister may not object to themselves")
    if obj["severity"] not in ALLOWED_SEVERITIES:
        raise ValueError("Invalid objection severity")
    if not isinstance(obj["objection"], str) or len(obj["objection"].strip()) == 0:
        raise ValueError("Objection text must be non-empty string")


def run_phase2(ministers_phase2: Optional[Dict[str, Callable]], positions: List[Dict[str, Any]], context_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run Phase 2: collect objections from ministers. Each minister may issue 0-2 objections.

    ministers_phase2: mapping minister_name -> callable(context_state, positions) -> List[objections]
    If None, returns empty list.
    """
    if not ministers_phase2:
        return []

    active = [p["minister"] for p in positions]
    all_objs: List[Dict[str, Any]] = []
    for mname, fn in ministers_phase2.items():
        objs = []
        if callable(fn):
            objs = fn(context_state, positions)
        elif isinstance(fn, list):
            objs = fn
        # Enforce list and cap
        if not isinstance(objs, list):
            raise ValueError("Minister objections must be a list")
        if len(objs) > 2:
            raise ValueError("Minister may issue at most 2 objections")

        seen_against = set()
        for o in objs:
            validate_objection(o, mname, active)
            if o["against"] in seen_against:
                raise ValueError("No repeated objections against same target allowed")
            seen_against.add(o["against"])
            all_objs.append(o)

    return all_objs


# --- Phase 3: Weighting ------------------------------------------------------
def compute_minister_weights(minister_positions: List[Dict[str, Any]], context_state: Dict[str, Any]) -> Dict[str, float]:
    weights: Dict[str, float] = {}
    for pos in minister_positions:
        m = pos["minister"]
        w = _effective_weight(m, pos.get("confidence", 0.0), context_state)
        weights[m] = w
    return weights


# --- Phase 5: Finalization ---------------------------------------------------
SILENCE_STRING = "NO ADVICE — SILENCE IS OPTIMAL"


def run_full_darbar(
    decision_id: str,
    context_state: Dict[str, Any],
    ministers_phase1: Dict[str, Any],
    decision_question: str,
    ministers_phase2: Optional[Dict[str, Callable]] = None,
    gatekeeper: Optional[Any] = None,
    prime_confidant: Optional[object] = None,
) -> Any:
    """
    Run the full Darbar simulation (Phases 0,1,2,3,4,5) with enforcement preconditions.

    ministers_phase1: mapping minister_name -> callable|dict (position)
    ministers_phase2: mapping minister_name -> callable returning objections list
    gatekeeper: Gatekeeper instance (required) — must have budget exhausted
    """
    # Preconditions
    conf = context_state.get("confidence_map", {}).get("overall_context_confidence", 0.0)
    if conf < 0.65:
        raise RuntimeError("Precondition failed: confidence below 0.65")
    unstable = context_state.get("confidence_map", {}).get("unstable_fields", [])
    if unstable:
        raise RuntimeError("Precondition failed: unstable fields present")
    if gatekeeper is None:
        raise RuntimeError("Gatekeeper instance required and must have budget exhausted")
    # require budget frozen: either max_questions==0 or history >= max
    if not (getattr(gatekeeper, "max_questions", 0) == 0 or len(getattr(gatekeeper, "question_history", [])) >= getattr(gatekeeper, "max_questions", 0)):
        raise RuntimeError("Precondition failed: Gatekeeper budget not exhausted/frozen")

    # Phase 0
    # Determine active ministers via Gatekeeper classifier wrapper (text -> ministers)
    active_ministers = []
    try:
        if gatekeeper is None:
            raise RuntimeError("Gatekeeper instance required and must have budget exhausted")
        # Use the decision question text to request the active minister set
        active_ministers = gatekeeper.ministers_from_text(decision_question, prime_confidant=prime_confidant)
    except Exception:
        # If classification fails, fall back to provided ministers mapping keys
        active_ministers = list(ministers_phase1.keys())

    docket = convocation(decision_id, context_state, active_ministers)

    # Filter ministers_phase1 to only those in the active quorum (quorum model)
    ministers_for_phase1 = {k: v for k, v in ministers_phase1.items() if k in set(active_ministers)}
    if not ministers_for_phase1:
        # No activated ministers — silence is optimal
        return SILENCE_STRING

    # Phase 1 (only activated ministers participate)
    positions = run_phase1(decision_id, context_state, ministers_for_phase1, decision_question)

    # Phase 2
    objections = run_phase2(ministers_phase2, positions, context_state)

    # Phase 3 weights
    weights = compute_minister_weights(positions, context_state)

    # Phase 4 synthesize
    synth_out = synthesize(decision_id, context_state, positions, objections)
    # validate synthesizer output
    validate_synthesizer_output(synth_out, positions)

    # Phase 5 finalization
    if synth_out.get("verdict") == "NO_ACTION":
        return SILENCE_STRING
    return synth_out

