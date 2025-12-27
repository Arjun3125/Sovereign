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
