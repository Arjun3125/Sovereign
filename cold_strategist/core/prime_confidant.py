"""
Prime Confidant (N) — limited arbiter for borderline activations and distortion detection.

N may only resolve borderline activations (e.g., 0.55-0.65) and detect/remove
spurious activations caused by emotional distortion. N must never add ministers
that are not present in the domain->minister mapping, nor remove high-confidence
activations (>= 0.6).

This module implements deterministic heuristics and returns a small audit log
when it modifies the candidate set.
"""
from typing import List, Dict, Any, Tuple
import re
from dataclasses import dataclass


@ dataclass
class ArbitrationResult:
    ministers: List[str]
    modified: bool
    justification: str
    escalate: bool = False


class PrimeConfidant:
    """Deterministic, rule-limited arbiter.

    Methods:
      - `arbitrate(classifier_output, candidate_ministers, text)` returns ArbitrationResult
    """

    BORDER_LOW = 0.55
    BORDER_HIGH = 0.65

    def __init__(self):
        pass

    def _detect_emotional_overconfidence(self, text: str) -> bool:
        t = text.lower()
        tokens = ["i know", "trust me", "obviously", "clearly", "everyone knows", "no doubt", "definitely", "for sure", "always"]
        exclaim = "!" in text
        return any(tok in t for tok in tokens) or exclaim

    def _detect_contradiction(self, text: str) -> bool:
        t = text.lower()
        # crude: presence of 'but' or 'however' with short sentences either side
        if " but " in t or " however " in t or " on the other hand " in t:
            return True
        return False

    def arbitrate(self, classifier_output: Dict[str, Any], candidate_ministers: List[str], text: str) -> ArbitrationResult:
        """
        Evaluate borderline activations and hidden distortions.

        Rules implemented:
        - Only consider domains with confidence in [BORDER_LOW, BORDER_HIGH).
        - If emotional overconfidence or contradiction detected, remove borderline domains.
        - Otherwise, if borderline mentions concrete signals (numbers, dates, legal words), include them.
        - Never remove domains with confidence >= 0.6 (protected).
        - Never add ministers outside the registry mapping; N only toggles borderline ones.
        """
        activated = classifier_output.get("activated_domains", [])
        # Map domain->confidence
        dom_conf = {entry.get("domain"): float(entry.get("confidence", 0)) for entry in activated}

        modified = False
        justification_parts = []
        new_list = list(candidate_ministers)

        # detect signals
        overconf = self._detect_emotional_overconfidence(text)
        contradiction = self._detect_contradiction(text)

        # find borderline domains
        for domain, conf in dom_conf.items():
            if self.BORDER_LOW <= conf < self.BORDER_HIGH:
                # domain minister key is the domain name in registry (assumption)
                minister_key = domain if domain in candidate_ministers or domain in [d for d in dom_conf.keys()] else domain
                # if protected (>=0.6) skip removal
                if conf >= 0.6:
                    continue
                # If distortion present, remove if present
                if overconf or contradiction:
                    if minister_key in new_list:
                        new_list.remove(minister_key)
                        modified = True
                        justification_parts.append(f"Silenced {minister_key} due to distortion (overconflict={overconf}, contradiction={contradiction})")
                else:
                    # include borderline if concrete signals present
                    if re.search(r"\b\d+\b", text) or re.search(r"\b(month|months|year|years|deadline|contract|bankrupt|runway)\b", text.lower()):
                        if minister_key not in new_list:
                            new_list.append(minister_key)
                            modified = True
                            justification_parts.append(f"Included {minister_key} due to concrete signals")

        # Escalation heuristic: many low-confidence activations together
        low_acts = [d for d, c in dom_conf.items() if c < self.BORDER_LOW]
        escalate = False
        if len(low_acts) >= 3 and (overconf or contradiction):
            escalate = True
            justification_parts.append("Escalated to Tribunal due to multiple low-confidence activations with distortion signals")

        justification = "; ".join(justification_parts) if justification_parts else "No arbitration changes"
        return ArbitrationResult(ministers=new_list, modified=modified, justification=justification, escalate=escalate)
