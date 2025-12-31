REENTRY_RULES = {
    "to_cooldown": {
        "conditions": [
            "war_decision_resolved",
            "override_acknowledged_or_not_needed"
        ]
    },
    "to_stabilize": {
        "conditions": [
            "emotional_load < 0.6",
            "urgency < 0.5"
        ],
        "min_events": 2
    },
    "to_standard_ready": {
        "conditions": [
            "no_war_triggers",
            "no_escalation_flags"
        ],
        "min_events": 3
    }
}
