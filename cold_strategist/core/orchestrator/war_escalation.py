from typing import List, Tuple
from core.rag.conflict_severity import CONFLICT_SEVERITY

WAR_ESCALATION_RULES = {
    "observe": 0,
    "caution": 2,
    "escalate": 4,
    "critical": 6,
}


def compute_conflict_score(conflicts: List[str]) -> int:
    score = 0
    for c in conflicts:
        score += CONFLICT_SEVERITY.get(c, 1)
    return score


class WarEscalationEngine:
    def evaluate(self, conflicts: List[str]) -> Tuple[str, int]:
        score = compute_conflict_score(conflicts)

        if score >= WAR_ESCALATION_RULES["critical"]:
            return "critical", score
        if score >= WAR_ESCALATION_RULES["escalate"]:
            return "escalate", score
        if score >= WAR_ESCALATION_RULES["caution"]:
            return "caution", score
        return "observe", score
