# minister_contracts.py
# MINISTER CONTRACTS — Hard governance boundaries per minister

import json
from typing import Dict, List, Any

# ===== CANONICAL MINISTER OUTPUT SCHEMA (MANDATORY) =====

MINISTER_OUTPUT_SCHEMA = {
    "minister": str,
    "position": str,  # ≤120 words
    "citations": [
        {
            "doctrine_id": str,
            "book": str,
            "similarity": float,  # 0.0-1.0
        }
    ],
    "confidence": float,  # 0.0-1.0
    "risk_flags": [str],
    "silence_recommended": bool,
    "escalation_required": bool,
}

# ===== MINISTER JURISDICTION CONTRACTS =====

MINISTER_CONTRACTS = {
    "psychology": {
        "may_address": [
            "bias",
            "fear",
            "overconfidence",
            "deception",
        ],
        "may_not_address": [
            "actions",
            "tactics",
            "timelines",
        ],
        "required_flags": ["cognitive_bias"],
        "auto_silence_if": [
            "no_psychology_tagged_doctrine",
        ],
    },

    "power": {
        "may_address": [
            "leverage",
            "asymmetry",
            "dominance",
            "reputation",
        ],
        "may_not_address": [
            "moral_judgments",
            "emotional_language",
            "long_term_planning",
        ],
        "escalate_if": [
            "power_gain_implies_irreversible_harm",
        ],
    },

    "conflict": {
        "may_address": [
            "escalation",
            "coercion",
            "deterrence",
            "violence_risk",
        ],
        "must_include": [
            "downside_assessment",
            "casualty_estimate",
        ],
        "auto_escalate_if": [
            "physical_harm_implied",
            "confidence_below_0.6",
        ],
    },

    "diplomacy": {
        "may_address": [
            "alliances",
            "negotiation",
            "signaling",
            "compromise",
        ],
        "may_not_address": [
            "coercion",
        ],
        "must_not_recommend": [
            "deception_without_doctrine",
        ],
        "auto_silence_if": [
            "no_diplomacy_tagged_doctrine",
        ],
    },

    "optionality": {
        "may_address": [
            "exits",
            "reversibility",
            "delay",
            "hedging",
        ],
        "must": [
            "propose_reversible_path_or_silence",
        ],
        "auto_silence_if": [
            "situation_already_irreversible",
        ],
    },

    "timing": {
        "may_address": [
            "patience",
            "windows",
            "urgency",
            "delay",
        ],
        "must_state": [
            "act_now_or_wait",
        ],
        "auto_silence_if": [
            "doctrine_disagreement_above_threshold",
        ],
    },

    "truth": {
        "role": "non_advisory",
        "may": [
            "flag_contradictions",
            "flag_weak_doctrine",
            "flag_self_deception",
            "lower_global_confidence",
        ],
        "may_not": [
            "recommend_actions",
            "break_ties",
        ],
        "escalate_if": [
            "cited_doctrine_similarity_below_0.5",
            "cross_book_contradiction",
        ],
    },

    "strategy": {
        "may_address": [
            "long_term_planning",
            "systems",
            "competitive_positioning",
            "execution",
        ],
        "may_not_address": [
            "immediate_tactics",
            "emotional_states",
        ],
    },
}

# ===== CONFIDENCE RULES (GLOBAL) =====

CONFIDENCE_THRESHOLDS = {
    "silence_recommended": 0.4,  # < 0.4 → recommend silence
    "escalation_required": 0.3,  # < 0.3 → must escalate
    "eligible_for_recommendation": 0.6,  # > 0.6 → can recommend
}


def validate_minister_output(output: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate minister output against schema.
    
    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    if "minister" not in output:
        return False, "Missing 'minister' field"
    
    if "position" not in output:
        return False, "Missing 'position' field"
    
    if "citations" not in output or not isinstance(output["citations"], list):
        return False, "Missing or invalid 'citations' field (must be non-empty list)"
    
    if not output["citations"]:
        return False, "citations list is empty (must have >= 1)"
    
    if "confidence" not in output:
        return False, "Missing 'confidence' field"
    
    # Validate confidence
    conf = output.get("confidence", -1)
    if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
        return False, f"confidence must be 0.0–1.0, got {conf}"
    
    # Validate position length
    pos = output.get("position", "")
    if len(pos.split()) > 120:
        return False, f"position exceeds 120 words ({len(pos.split())} words)"
    
    # Validate citations
    for i, cite in enumerate(output["citations"]):
        if "doctrine_id" not in cite or "book" not in cite or "similarity" not in cite:
            return False, f"citation[{i}] missing required fields (doctrine_id, book, similarity)"
        
        sim = cite.get("similarity", -1)
        if not isinstance(sim, (int, float)) or sim < 0.0 or sim > 1.0:
            return False, f"citation[{i}] similarity must be 0.0–1.0, got {sim}"
    
    # Validate risk_flags
    if "risk_flags" in output and not isinstance(output["risk_flags"], list):
        return False, "risk_flags must be a list"
    
    # Validate boolean fields
    for field in ["silence_recommended", "escalation_required"]:
        if field in output and not isinstance(output[field], bool):
            return False, f"{field} must be boolean"
    
    return True, ""


def compute_base_confidence(
    similarity_scores: List[float],
    doctrine_count: int,
    agreement_score: float = 1.0,
) -> float:
    """
    Compute base confidence from doctrine metrics.
    
    Args:
        similarity_scores: list of similarity scores [0.0-1.0]
        doctrine_count: number of distinct doctrines cited
        agreement_score: cross-doctrine agreement [0.0-1.0]
    
    Returns:
        confidence value [0.0-1.0]
    """
    if not similarity_scores:
        return 0.0
    
    avg_similarity = sum(similarity_scores) / len(similarity_scores)
    doctrine_factor = min(doctrine_count / 3.0, 1.0)  # max out at 3 doctrines
    
    confidence = avg_similarity * doctrine_factor * agreement_score
    return min(max(confidence, 0.0), 1.0)


def should_silence(confidence: float, reason: str = "") -> bool:
    """
    Determine if output should be silenced.
    
    Args:
        confidence: computed confidence [0.0-1.0]
        reason: optional reason for silence
    
    Returns:
        True if silence is recommended
    """
    return confidence < CONFIDENCE_THRESHOLDS["silence_recommended"]


def should_escalate(confidence: float, risk_flags: List[str] = None) -> bool:
    """
    Determine if output should escalate to Tribunal.
    
    Args:
        confidence: computed confidence [0.0-1.0]
        risk_flags: list of risk flags from minister
    
    Returns:
        True if escalation is required
    """
    if confidence < CONFIDENCE_THRESHOLDS["escalation_required"]:
        return True
    
    if risk_flags:
        escalation_triggers = [
            "irreversible_harm",
            "physical_harm",
            "legal_risk",
            "existential_risk",
        ]
        if any(flag in risk_flags for flag in escalation_triggers):
            return True
    
    return False


# ===== HARD RULE: Output Gate =====

def gate_minister_output(output: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """
    Final validation gate before output reaches Darbar.
    
    If invalid → discard silently.
    If valid → return True + output.
    
    Returns:
        (is_valid, output)
    """
    is_valid, error = validate_minister_output(output)
    if not is_valid:
        print(f"[GATE] Discarding invalid minister output: {error}")
        return False, {}
    
    return True, output
