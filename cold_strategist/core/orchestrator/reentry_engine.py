from typing import Dict, Any
from core.orchestrator.reentry_states import REENTRY_STATES


class Signals:
    def __init__(self, resolved: bool = False, stable_events: int = 0, no_war_flags: bool = False):
        self.resolved = resolved
        self.stable_events = stable_events
        self.no_war_flags = no_war_flags


class ReentryEngine:
    def evaluate(self, state: str, signals: Signals) -> str:
        # Deterministic transitions
        if state == "WAR_ACTIVE" and signals.resolved:
            return "COOLDOWN"

        if state == "COOLDOWN" and signals.stable_events >= 2:
            return "STABILIZE"

        if state == "STABILIZE" and signals.no_war_flags:
            return "STANDARD_READY"

        return state
