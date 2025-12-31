from typing import Dict, List, Any, Optional


class ConvergenceEngine:
    """Attempt to compute a middle-ground strategy from multiple stances."""

    def converge(self, stances: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """Try to find a middle ground by extracting shared constraints.

        Returns a dict with type 'middle_ground' and constraints when found, else None.
        """
        shared = self.shared_constraints(stances)
        if shared:
            return {"type": "middle_ground", "constraints": shared}
        return None

    def shared_constraints(self, stances: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        constraints = None
        for group in stances.values():
            for i in group:
                c = list(i.get("constraints") or [])
                if constraints is None:
                    constraints = set(c)
                else:
                    constraints &= set(c)
        return list(constraints) if constraints else []
class ConvergenceEngine:
    def converge(self, stances):
        """
        Try to find middle ground by intersecting constraints.
        stances: dict of stance -> list[intervention]
        """
        shared = self.shared_constraints(stances)
        if shared:
            return {
                "type": "middle_ground",
                "constraints": shared
            }
        return None

    def shared_constraints(self, stances):
        constraints = None
        for group in stances.values():
            for i in group:
                if constraints is None:
                    constraints = set(i.get("constraints", []))
                else:
                    constraints &= set(i.get("constraints", []))
        return list(constraints) if constraints else []
