from typing import List, Dict, Any
from core.debate.disagreement import detect_disagreement
from core.debate.convergence import ConvergenceEngine


class DisagreementResolver:
    """Resolve minister disagreements by convergence or ranked tradeoffs.

    Usage:
        resolver = DisagreementResolver()
        result = resolver.resolve(interventions)
    """

    def resolve(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        conflict, stances = detect_disagreement(interventions)
        if not conflict:
            return {"resolution": "none"}

        converger = ConvergenceEngine()
        middle = converger.converge(stances)

        if middle:
            return {"resolution": "converged", "strategy": middle}

        # fallback: ranked tradeoffs by confidence
        ranked = sorted(interventions, key=lambda x: float(x.get("confidence") or 0.0), reverse=True)
        return {"resolution": "tradeoffs", "ranked_options": ranked}
from core.debate.disagreement import detect_disagreement
from core.debate.convergence import ConvergenceEngine


class DisagreementResolver:
    def resolve(self, interventions):
        conflict, stances = detect_disagreement(interventions)
        if not conflict:
            return {"resolution": "none"}

        converger = ConvergenceEngine()
        middle = converger.converge(stances)

        if middle:
            return {
                "resolution": "converged",
                "strategy": middle
            }

        # fallback: ranked tradeoffs
        ranked = sorted(
            interventions,
            key=lambda x: x.get("confidence", 0.0),
            reverse=True
        )
        return {
            "resolution": "tradeoffs",
            "ranked_options": ranked
        }
