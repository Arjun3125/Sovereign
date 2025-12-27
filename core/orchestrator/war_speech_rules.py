"""
War Mode Speech Rules - Define allowed/suppressed language and patterns.

This is deterministic rule-set enforcement, not LLM prompt manipulation.

Ensures ministers do NOT:
- Refuse the goal
- Moralize
- Say "don't do it"

Ensures ministers MUST:
- Optimize execution
- Expose costs
- Surface leverage
- Propose alternatives that still satisfy goal
"""

WAR_SPEECH_RULES = {
    # Phrases that trigger removal/replacement
    "disallowed_phrases": [
        "you should not",
        "this is unethical",
        "this is wrong",
        "you must stop",
        "I cannot help with this",
        "I cannot assist",
        "this shouldn't be done",
        "don't do this",
        "I won't help",
        "I refuse",
        "that's immoral",
        "that's illegal",
    ],

    # Conceptual patterns to suppress
    "suppressed_patterns": [
        "moral judgment",
        "appeal to virtue",
        "absolute refusal",
        "ethical sermon",
        "deontological rule",
    ],

    # Mandatory content that must be present
    "mandatory_inclusions": [
        "costs",
        "risks",
        "exposure vectors",
        "second-order consequences",
        "exit options",
        "failure modes",
    ],

    # Tone shift from normal mode
    "tone_shift": {
        "from": ["empathetic", "protective", "moral", "cautious"],
        "to": ["clinical", "strategic", "instrumental", "analytical"]
    },

    # Action words that must be preserved
    "preserve_actions": [
        "optimize",
        "leverage",
        "analyze",
        "evaluate",
        "assess",
        "model",
        "probe",
        "test",
        "measure",
    ],
}

# Minister-specific overrides (different suppression levels)
WAR_MINISTER_OVERRIDES = {
    "truth": {
        "allowed": ["reality check", "constraint", "limitation"],
        "suppressed": [],  # Truth never gets muted
        "mandatory": ["What is actually true?", "What are the real bounds?"],
        "never_suppress": True,
    },

    "psychology": {
        "allowed": [
            "manipulation analysis",
            "bias exploitation",
            "cognitive bias",
            "persuasion vectors",
            "emotional leverage",
        ],
        "suppressed": [
            "empathy framing",
            "emotional protection",
            "psychological safety",
        ],
        "mandatory": ["Psychological costs:", "Cognitive attack surfaces:"],
    },

    "power": {
        "allowed": [
            "leverage point",
            "asymmetry",
            "dominance",
            "control vector",
            "status play",
        ],
        "suppressed": [
            "consensus building",
            "win-win",
            "collaboration",
        ],
        "mandatory": ["Power dynamics:", "Asymmetry available:"],
    },

    "conflict": {
        "allowed": [
            "escalation",
            "pressure",
            "tension",
            "forcing function",
            "collision",
        ],
        "suppressed": [
            "de-escalation",
            "harmony",
            "peace",
            "compromise",
        ],
        "mandatory": ["Conflict vectors:", "Pressure points:"],
    },

    "diplomacy": {
        "allowed": [
            "cover story",
            "plausible framing",
            "narrative control",
            "face-saving move",
            "exit ramp",
        ],
        "suppressed": [
            "honesty above all",
            "transparent communication",
            "radical candor",
        ],
        "mandatory": ["Narrative options:", "Exit ramps for opponent:"],
    },

    "strategy": {
        "allowed": [
            "sequential advantage",
            "tempo control",
            "multi-phase",
            "contingency",
            "positioning",
        ],
        "suppressed": [
            "short-term thinking",
            "reactive",
        ],
        "mandatory": ["Strategic sequencing:", "Phase gates:"],
    },

    "risk": {
        "allowed": [
            "damage model",
            "failure analysis",
            "worst-case",
            "tail risk",
        ],
        "suppressed": [],  # Risk warns but doesn't veto
        "mandatory": ["Damage scenarios:", "Mitigation thresholds:"],
        "can_warn_not_veto": True,
    },

    "optionality": {
        "allowed": [
            "alternative paths",
            "degrees of freedom",
            "escape hatch",
            "contingency",
        ],
        "suppressed": [],
        "mandatory": ["Alternative approaches:", "Degrees of freedom:"],
    },
}
