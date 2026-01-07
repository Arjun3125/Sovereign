"""
Minister Registry - Canonical Minister Domains (LOCKED)

Static. Never changes. Each minister owns specific analytical domains.
This file is the source of truth for minister-to-domain mapping.
"""

# ============================================================================
# CANONICAL MINISTER REGISTRY
# ============================================================================

MINISTERS = {
    "power": [
        "leverage",
        "reputation",
        "thresholds",
        "optics",
        "dominance",
        "asymmetry"
    ],
    
    "psychology": [
        "bias",
        "emotion",
        "self-deception",
        "manipulation",
        "cognitive-distortion",
        "motivation"
    ],
    
    "conflict": [
        "force",
        "deterrence",
        "escalation",
        "decisiveness",
        "adversarial-analysis",
        "coercion"
    ],
    
    "diplomacy": [
        "alliances",
        "negotiation",
        "repeated-games",
        "cooperation",
        "trust",
        "communication"
    ],
    
    "risk": [
        "ruin",
        "irreversibility",
        "tail-risk",
        "catastrophe",
        "survival",
        "hedging"
    ],
    
    "optionality": [
        "exit",
        "liquidity",
        "retreat",
        "lock-in",
        "flexibility",
        "reversibility"
    ],
    
    "timing": [
        "tempo",
        "windows",
        "patience",
        "urgency",
        "seasons",
        "rhythm"
    ],
    
    "technology": [
        "automation",
        "systems",
        "leverage-tools",
        "capability",
        "efficiency",
        "obsolescence"
    ],
    
    "data": [
        "probability",
        "signal",
        "uncertainty",
        "evidence",
        "measurement",
        "noise"
    ],
    
    "adaptation": [
        "change",
        "obsolescence",
        "pivot",
        "evolution",
        "resilience",
        "learning"
    ],
    
    "discipline": [
        "execution",
        "systems",
        "follow-through",
        "consistency",
        "accountability",
        "methodology"
    ],
    
    "legitimacy": [
        "norms",
        "authority",
        "moral-framing",
        "consent",
        "justification",
        "sustainability"
    ],
    
    "truth": [
        "ground-reality",
        "feedback",
        "delusion-detection",
        "accuracy",
        "verification",
        "calibration"
    ],
    
    "intelligence": [
        "information",
        "secrecy",
        "deception",
        "reconnaissance",
        "awareness",
        "blind-spots"
    ]
}


# ---------------------------------------------------------------------------
# Extended Minister Set (18 ministers) and Activation Helpers
# ---------------------------------------------------------------------------
# Add additional ministers referenced by the Full 18-Minister Activation Matrix.
# We keep existing keys and add aliases / new ministers where appropriate.
MINISTERS.setdefault("survival", [
    "existential",
    "irrecoverable",
    "do-or-die",
    "last-chance",
])

MINISTERS.setdefault("operations", [
    "execution",
    "logistics",
    "capacity",
    "coordination",
    "discipline",
])

MINISTERS.setdefault("strategy", [
    "long-term",
    "vision",
    "trajectory",
    "empire",
    "future",
])

MINISTERS.setdefault("narrative", [
    "perception",
    "story",
    "public",
    "image",
    "reputation",
])

MINISTERS.setdefault("ethics", [
    "moral",
    "right",
    "wrong",
    "guilt",
    "conscience",
])

MINISTERS.setdefault("finance", [
    "capital",
    "money",
    "cost",
    "roi",
    "investment",
    "cash flow",
])

MINISTERS.setdefault("time", [
    "deadline",
    "runway",
    "months",
    "years",
])

MINISTERS.setdefault("legal", [
    "law",
    "contract",
    "compliance",
    "regulation",
    "litigation",
])

MINISTERS.setdefault("prime_confidant", [
    "overconfidence",
    "contradiction",
    "emotional_distortion",
])

MINISTERS.setdefault("tribunal", [
    "deadlock",
    "override",
    "freeze",
    "appeal",
])


# ============================================================================
# Darbar Activation Map & Ollama Classifier Prompt
# ============================================================================
DARBAR_MODES = ("QUORUM", "FULL_PARLIAMENT")
DEFAULT_DARBAR_MODE = "QUORUM"

# By default, activation conditions mirror minister domains; this map allows
# targeted signal-driven activation keywords per the Full 18-Minister Matrix.
ACTIVATION_MAP = {m: list(domains) for m, domains in MINISTERS.items()}

# Tiered extensions (explicit signals recommended by the constitutional matrix)
ACTIVATION_MAP.setdefault("risk", []).extend([
    "loss",
    "ruin",
    "wipeout",
    "downside",
    "drawdown",
    "bankruptcy",
    "irreversible",
])
ACTIVATION_MAP.setdefault("truth", []).extend([
    "assumption",
    "estimate",
    "believe",
    "unclear",
    "guess",
    "narrative",
])
ACTIVATION_MAP.setdefault("power", []).extend([
    "leverage",
    "dominance",
    "control",
    "authority",
    "optics",
    "hierarchy",
])
ACTIVATION_MAP.setdefault("optionality", []).extend([
    "exit",
    "flexibility",
    "reversibility",
    "fallback",
    "pivot",
])
ACTIVATION_MAP.setdefault("operations", []).extend([
    "execution",
    "logistics",
    "capacity",
    "coordination",
])
ACTIVATION_MAP.setdefault("data", []).extend([
    "probability",
    "signal",
    "noise",
    "metrics",
    "data",
])
ACTIVATION_MAP.setdefault("strategy", []).extend([
    "long-term",
    "vision",
    "trajectory",
])
ACTIVATION_MAP.setdefault("psychology", []).extend([
    "fear",
    "ego",
    "bias",
    "emotion",
])
ACTIVATION_MAP.setdefault("diplomacy", []).extend([
    "negotiate",
    "alliance",
    "partner",
    "compromise",
])
ACTIVATION_MAP.setdefault("narrative", []).extend([
    "perception",
    "story",
    "public",
    "image",
])
ACTIVATION_MAP.setdefault("ethics", []).extend([
    "moral",
    "guilt",
    "conscience",
])
ACTIVATION_MAP.setdefault("finance", []).extend([
    "capital",
    "money",
    "cost",
    "roi",
])
ACTIVATION_MAP.setdefault("time", []).extend([
    "deadline",
    "runway",
])
ACTIVATION_MAP.setdefault("technology", []).extend([
    "system",
    "automation",
    "ai",
])
ACTIVATION_MAP.setdefault("legal", []).extend([
    "law",
    "contract",
])


# Ollama classifier prompt (paste-ready). Ollama should output JSON only.
OLLAMA_CLASSIFIER_PROMPT = """
You are a domain activation classifier.

Input: a decision statement or context text.

Your task:
- Identify which strategic domains are explicitly or implicitly activated
- Match based on keywords, intent, and risk signals
- Do NOT give advice
- Do NOT explain reasoning

Output ONLY JSON.

Domains (fixed list):
[risk, survival, truth, timing, power, optionality, operations, data_signals, strategy, psychology, diplomacy, narrative, finance, time, technology, legal, ethics]

For each activated domain, return:
- domain
- confidence (0.0–1.0)

Example Output
{
  "activated_domains": [
    {"domain": "risk", "confidence": 0.91},
    {"domain": "finance", "confidence": 0.87},
    {"domain": "power", "confidence": 0.64}
  ]
}
"""


def get_activation_conditions(minister: str) -> list:
    """
    Return the activation keywords/conditions for `minister`.
    """
    return ACTIVATION_MAP.get(minister, [])


def active_ministers_for_context(context_fields: list, mode: str = DEFAULT_DARBAR_MODE) -> list:
    """
    Determine which ministers should be active for a given frozen context.

    Args:
        context_fields: list of canonical field keys or extracted activation keywords.
        mode: one of the DARBAR_MODES. In `FULL_PARLIAMENT` all ministers are returned.

    Returns:
        List of minister names that are activated for the provided context.
    """
    if mode == "FULL_PARLIAMENT":
        return all_ministers()

    if not context_fields:
        return []

    ctx_set = set([c.lower() for c in context_fields])
    active = []
    for minister, conditions in ACTIVATION_MAP.items():
        cond_set = set([c.lower() for c in conditions])
        if ctx_set.intersection(cond_set):
            active.append(minister)
    return active


def is_minister_active(minister: str, context_fields: list, mode: str = DEFAULT_DARBAR_MODE) -> bool:
    """Return True if `minister` is active given the context and mode."""
    if mode == "FULL_PARLIAMENT":
        return True
    return minister in active_ministers_for_context(context_fields, mode)


def active_from_classifier_output(classifier_output: dict, threshold: float = 0.6, mode: str = DEFAULT_DARBAR_MODE) -> list:
    """
    Convert Ollama classifier JSON output to an active minister list.

    Args:
        classifier_output: parsed JSON from Ollama with key 'activated_domains'
        threshold: confidence threshold for activation
        mode: DARBAR mode

    Returns:
        List of minister names selected by domain->minister lookup and threshold.
    """
    if mode == "FULL_PARLIAMENT":
        return all_ministers()

    activated = classifier_output.get("activated_domains") or []
    result = set()
    for entry in activated:
        domain = entry.get("domain")
        conf = float(entry.get("confidence", 0))
        if conf >= threshold and domain:
            # canonicalize domain keys to minister keys where possible
            lookup = domain
            if lookup == "data_signals":
                lookup = "data"
            if lookup in MINISTERS:
                result.add(lookup)
            else:
                # attempt fuzzy match to existing ministers
                if lookup in ACTIVATION_MAP:
                    result.add(lookup)
    return sorted(result)


def get_minister_domains(minister: str) -> list:
    """
    Get the domains owned by a specific minister.
    
    Args:
        minister: Minister name
        
    Returns:
        List of domain keywords, or empty list if minister not found
    """
    return MINISTERS.get(minister, [])


def all_ministers() -> list:
    """Get list of all minister names."""
    return list(MINISTERS.keys())


def domain_to_ministers(domain: str) -> list:
    """
    Get which ministers own a specific domain.
    
    Args:
        domain: Domain keyword
        
    Returns:
        List of minister names covering this domain
    """
    result = []
    for minister, domains in MINISTERS.items():
        if domain in domains:
            result.append(minister)
    return result
