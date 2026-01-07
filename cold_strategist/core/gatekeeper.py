"""
Gatekeeper - Enforces question permission logic for ContextBuilder/Darbar

Implements the enforcement-grade rules provided by the user.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time
from cold_strategist.core.selection import minister_registry as registry


@dataclass
class Gatekeeper:
    decision_id: str
    question_history: List[Dict[str, Any]] = field(default_factory=list)
    max_questions: int = 3
    recent_repeat_n: int = 2

    def can_ask(self, request: Dict[str, Any], context_state: Dict[str, Any], active_required_fields: Dict[str, List[str]], active_ministers: List[str]) -> Dict[str, Any]:
        """
        Evaluate whether a clarification question may be asked.

        request: {
            "requester": str,
            "requested_field": str,
            "reason": str,
            "decision_id": str,
            "context_snapshot": {...}
        }

        Returns a dict with either {"status":"ALLOWED"} or {"status":"REJECTED","reason":...}
        """
        # A. Budget checks
        if len(self.question_history) >= self.max_questions:
            return {"status": "REJECTED", "reason": "BUDGET_EXHAUSTED"}

        # B. Basic shape
        requester = request.get("requester")
        field = request.get("requested_field")
        if not requester or not field:
            return {"status": "REJECTED", "reason": "MALFORMED_REQUEST"}

        # C. Field validity: must exist in canonical context_state root or nested keys
        if not self._field_exists(field, context_state):
            return {"status": "REJECTED", "reason": "FIELD_INVALID"}

        # D. Required for at least one active minister
        required_for = [m for m, reqs in active_required_fields.items() if field in reqs]
        if not any(m in active_ministers for m in required_for):
            return {"status": "REJECTED", "reason": "FIELD_NOT_REQUIRED_BY_ACTIVE_MINISTER"}

        # E. Missing or unstable
        field_entry = self._get_field_entry(field, context_state)
        if field_entry is None:
            # Missing entirely -> allowed (subject to other checks)
            pass
        else:
            value = field_entry.get("value")
            confidence = float(field_entry.get("confidence", 0.0) or 0.0)
            stable = bool(field_entry.get("stable", False))
            if value is not None and stable and confidence >= 0.6:
                return {"status": "REJECTED", "reason": "FIELD_ALREADY_STABLE"}

        # F. Jurisdiction match: requester must be allowed to request this field
        if not self._jurisdiction_allows(requester, field):
            return {"status": "REJECTED", "reason": "JURISDICTION_MISMATCH"}

        # G. Singular scope: ensure field is a single canonical path (no commas)
        if "," in field or " and " in field:
            return {"status": "REJECTED", "reason": "SINGULAR_SCOPE_VIOLATION"}

        # H. No redundancy: check last N turns
        recent = self.question_history[-self.recent_repeat_n:]
        for q in recent:
            if q.get("requested_field") == field and q.get("status") == "REJECTED":
                return {"status": "REJECTED", "reason": "PREVIOUSLY_REFUSED"}

        # I. Hard reject pattern matching for open-ended or forbidden wording
        if self._is_open_ended(request.get("reason", "")):
            return {"status": "REJECTED", "reason": "OPEN_ENDED_OR_OUT_OF_SCOPE"}

        # Passed all checks: record tentative allowed question
        entry = {
            "timestamp": time.time(),
            "requester": requester,
            "requested_field": field,
            "reason": request.get("reason"),
            "status": "ALLOWED"
        }
        self.question_history.append(entry)
        return {"status": "ALLOWED"}

    def record_rejection(self, request: Dict[str, Any], reason: str) -> None:
        self.question_history.append({
            "timestamp": time.time(),
            "requester": request.get("requester"),
            "requested_field": request.get("requested_field"),
            "reason": request.get("reason"),
            "status": "REJECTED",
            "reject_reason": reason
        })

    def _field_exists(self, field_path: str, context_state: Dict[str, Any]) -> bool:
        # Accept dotted paths like 'risk_profile.hard_loss_cap_percent'
        parts = field_path.split(".")
        node = context_state
        for p in parts:
            if not isinstance(node, dict) or p not in node:
                return False
            node = node[p]
        return True

    def _get_field_entry(self, field_path: str, context_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        parts = field_path.split(".")
        node = context_state
        for p in parts:
            if not isinstance(node, dict) or p not in node:
                return None
            node = node[p]
        return node if isinstance(node, dict) else None

    def _jurisdiction_allows(self, requester: str, field: str) -> bool:
        # Use the canonical minister registry to decide jurisdiction.
        if not requester:
            return False

        # Normalize common requester name formats to registry keys
        norm = requester.lower().strip()
        for prefix in ("minister_of_", "minister of ", "minister_", "minister-"):
            if norm.startswith(prefix):
                norm = norm[len(prefix):]
                break

        # If requester directly matches a minister key, consult its domains
        allowed_domains = registry.get_minister_domains(norm) if norm in registry.MINISTERS else []

        # If registry had no entry, try exact minister name match ignoring case
        if not allowed_domains:
            for m in registry.all_ministers():
                if m.lower() == norm:
                    allowed_domains = registry.get_minister_domains(m)
                    break

        # Root token of the field (e.g., 'risk_profile' from 'risk_profile.hard_loss')
        root = field.split(".")[0]

        # Allow if root is exactly the minister name
        if root.lower() == norm:
            return True

        # Check whether any allowed domain keyword appears in the field path
        field_tokens = set()
        for part in field.replace('-', '_').split('.'):
            for token in part.split('_'):
                field_tokens.add(token.lower())

        for dom in allowed_domains:
            if dom.lower() in field_tokens:
                return True

        # As a fallback, allow if requester equals a registered minister and there are domains (broad permission)
        if norm in registry.all_ministers() and allowed_domains:
            return True

        return False


    def ministers_from_text(self, text: str, threshold: float = 0.6, mode: str = registry.DEFAULT_DARBAR_MODE, use_ollama: bool = False, ollama_model: str = None, timeout: int = 8, prime_confidant: object = None) -> List[str]:
        """
        Helper: classify free-text using the activation classifier and return
        ministers that meet the Gatekeeper confidence threshold.

        This wraps `cold_strategist.core.activation.activate_from_text` so callers
        of Gatekeeper can obtain a vetted active-minister list directly.
        """
        try:
            from cold_strategist.core import activation as activation_module
        except Exception:
            return []
        # First obtain classifier output (raw) and initial candidate ministers
        classifier_output = activation_module.classify_text_with_options(text, use_ollama=use_ollama, ollama_model=ollama_model, timeout=timeout)
        candidates = activation_module.activate_from_text(text, threshold=threshold, mode=mode, use_ollama=use_ollama, ollama_model=ollama_model, timeout=timeout)

        # If a Prime Confidant is provided, let it arbitrate borderline cases
        if prime_confidant is not None:
            try:
                # The PrimeConfidant.arbitrate must return an object with ministers, modified, justification, escalate
                res = prime_confidant.arbitrate(classifier_output, list(candidates), text)
                # Only accept modifications that do not add ministers outside the candidate mapping
                final = []
                for m in res.ministers:
                    if m in candidates:
                        final.append(m)
                # If PrimeConfidant removed some, record justification in history
                if res.modified:
                    self.question_history.append({"timestamp": time.time(), "requester": "prime_confidant", "requested_field": None, "reason": res.justification, "status": "PRIME_CONFIDANT_ADJUSTMENT"})
                # If escalation flagged, add an audit entry
                if getattr(res, "escalate", False):
                    self.question_history.append({"timestamp": time.time(), "requester": "prime_confidant", "requested_field": None, "reason": "ESCALATE_TRIBUNAL", "status": "ESCALATED"})
                return sorted(final)
            except Exception:
                # On any failure, return original candidates
                return sorted(candidates)

        return sorted(candidates)

    def _is_open_ended(self, reason_text: str) -> bool:
        if not reason_text:
            return True
        lower = reason_text.lower()
        # Simple heuristics for forbidden patterns
        bad_tokens = ["why", "tell me more", "explain", "how do i", "opinion", "suggest"]
        return any(tok in lower for tok in bad_tokens)
