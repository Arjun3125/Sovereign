from typing import List, Dict, Any
from core.rag.conflict_triggers import detect_conflicts, Claim


class TruthAudit:
    def audit(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        audits = []
        for c in claims:
            # Normalize into Claim dataclass for detection
            claim = Claim(
                id=c.get("id") or c.get("claim_id"),
                assertion_strength=c.get("assertion_strength", 0.0),
                confidence_modifier=c.get("confidence_modifier", 1.0),
                context_tags=set(c.get("context_tags", [])),
                application_space=set(c.get("application_space", [])),
                mode=c.get("mode", "standard"),
                source_count=c.get("source_count", len(c.get("sources", []))),
                counter_citations=c.get("counter_citations", []),
            )

            conflicts = detect_conflicts(claim)
            if conflicts:
                audits.append({
                    "claim_id": claim.id,
                    "conflicts": conflicts,
                    "note": self._frame(conflicts, c),
                })

        return audits

    def _frame(self, conflicts: List[str], claim: Dict[str, Any]) -> str:
        if "STALE_EVIDENCE" in conflicts:
            return "Evidence supports the direction, but confidence should be moderated."
        return "Claim requires corroboration or scope adjustment."
