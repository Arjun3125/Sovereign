# tribunal_silence.py
# TRIBUNAL + SILENCE FORMALIZATION (Final Governance Layer F)

import json
from typing import Dict, List, Any, Literal
from enum import Enum


class TribunalVerdict(Enum):
    """Three verdicts only. No others."""
    ALLOW = "ALLOW"
    SILENCE = "SILENCE"
    ESCALATE = "ESCALATE"


class Tribunal:
    """
    Non-advisory body that judges validity of minister advice.
    Does NOT reason, create, or debate.
    Only judges constitutionality.
    """

    def __init__(self):
        self.last_verdict = None
        self.last_reasoning = None

    def judge(
        self,
        minister_outputs: List[Dict[str, Any]],
        doctrine_sources: List[Dict[str, Any]],
        user_query: str = "",
    ) -> Dict[str, Any]:
        """
        Judge validity of all minister outputs.
        
        Returns:
            {
                "verdict": "ALLOW" | "SILENCE" | "ESCALATE",
                "reason": "constitutional justification",
                "minority_warnings": [],
                "confidence": 0.0-1.0,
                "escalation_triggers": [],
            }
        """
        # Check automatic escalation triggers
        escalation_triggers = self._check_escalation_triggers(
            minister_outputs, doctrine_sources
        )

        if escalation_triggers:
            self.last_verdict = TribunalVerdict.ESCALATE
            self.last_reasoning = f"Automatic escalation: {'; '.join(escalation_triggers)}"
            return {
                "verdict": TribunalVerdict.ESCALATE.value,
                "reason": self.last_reasoning,
                "minority_warnings": [],
                "confidence": 0.2,
                "escalation_triggers": escalation_triggers,
            }

        # Check if silence is appropriate
        avg_confidence = self._compute_average_confidence(minister_outputs)
        if avg_confidence < 0.4:
            self.last_verdict = TribunalVerdict.SILENCE
            self.last_reasoning = f"Insufficient doctrine confidence ({avg_confidence:.2f})"
            return {
                "verdict": TribunalVerdict.SILENCE.value,
                "reason": self.last_reasoning,
                "minority_warnings": [],
                "confidence": avg_confidence,
                "escalation_triggers": [],
            }

        # Check for doctrine integrity issues
        integrity_issues = self._check_doctrine_integrity(doctrine_sources)
        if integrity_issues:
            self.last_verdict = TribunalVerdict.SILENCE
            self.last_reasoning = f"Doctrine integrity issue: {integrity_issues[0]}"
            return {
                "verdict": TribunalVerdict.SILENCE.value,
                "reason": self.last_reasoning,
                "minority_warnings": integrity_issues,
                "confidence": avg_confidence,
                "escalation_triggers": [],
            }

        # If we reach here, advice is allowed
        self.last_verdict = TribunalVerdict.ALLOW
        self.last_reasoning = f"Doctrine sound, confidence {avg_confidence:.2f}"
        return {
            "verdict": TribunalVerdict.ALLOW.value,
            "reason": self.last_reasoning,
            "minority_warnings": [],
            "confidence": avg_confidence,
            "escalation_triggers": [],
        }

    def _check_escalation_triggers(
        self,
        minister_outputs: List[Dict[str, Any]],
        doctrine_sources: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Check for automatic escalation triggers.
        
        Returns:
            List of escalation reason strings (empty if none triggered)
        """
        triggers = []

        # Trigger 1: Minister confidence < 0.3
        for m in minister_outputs:
            if m.get("confidence", 0.0) < 0.3:
                triggers.append(f"{m.get('minister', 'unknown')} confidence too low")

        # Trigger 2: Minister flags irreversible harm
        for m in minister_outputs:
            if "irreversible_harm" in m.get("risk_flags", []):
                triggers.append(f"{m.get('minister', 'unknown')} flagged irreversible harm")

        # Trigger 3: Ministry of Truth (if exists) flags contradiction
        for m in minister_outputs:
            if m.get("minister") == "truth" and m.get("escalation_required"):
                triggers.append("Ministry of Truth flagged contradiction")

        # Trigger 4: ≥2 ministers strongly disagree
        disagreement_count = sum(
            1 for m in minister_outputs if m.get("silence_recommended", False)
        )
        if disagreement_count >= 2:
            triggers.append(f"{disagreement_count} ministers recommend silence")

        # Trigger 5: Doctrine tagged 'warning' dominates
        warning_count = sum(
            1 for d in doctrine_sources if d.get("metadata", {}).get("risk_class") == "warning"
        )
        if warning_count > len(doctrine_sources) / 2:
            triggers.append("Warning-type doctrine dominates")

        return triggers

    def _check_doctrine_integrity(
        self, doctrine_sources: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Check for doctrine integrity issues.
        
        Returns:
            List of issue descriptions (empty if none)
        """
        issues = []

        # Check 1: Similarity < 0.5 on any cited doctrine
        for d in doctrine_sources:
            if d.get("similarity", 1.0) < 0.5:
                issues.append(
                    f"Weak doctrine: {d.get('doctrine_id', 'unknown')} "
                    f"(similarity: {d.get('similarity', 0):.2f})"
                )

        # Check 2: Cross-book contradiction
        books_cited = set(d.get("book") for d in doctrine_sources)
        if len(books_cited) > 1:
            # Placeholder: in production, compute semantic contradiction
            pass

        return issues

    def _compute_average_confidence(self, minister_outputs: List[Dict[str, Any]]) -> float:
        """Compute average confidence across all ministers."""
        if not minister_outputs:
            return 0.0
        
        confidences = [
            m.get("confidence", 0.0)
            for m in minister_outputs
            if isinstance(m.get("confidence"), (int, float))
        ]
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)


class SilenceManager:
    """
    Formal silence-as-action system.
    Silence is a first-class output, not a failure.
    """

    SILENCE_TEMPLATES = {
        "insufficient_doctrine": (
            "No advice is optimal.\n\n"
            "WHY:\n"
            "– Doctrine is insufficient\n"
            "– Cross-book disagreement\n"
            "– Confidence too low\n\n"
            "RECOMMENDED POSTURE:\n"
            "– Maintain optionality\n"
            "– Observe longer\n"
            "– Re-evaluate conditions"
        ),
        "irreversible_harm": (
            "No advice is optimal.\n\n"
            "WHY:\n"
            "– Proposed action is irreversible\n"
            "– Downside asymmetric\n"
            "– Doctrine warns against commitment\n\n"
            "RECOMMENDED POSTURE:\n"
            "– Postpone decision\n"
            "– Increase information\n"
            "– Preserve exits"
        ),
        "contradiction": (
            "No advice is optimal.\n\n"
            "WHY:\n"
            "– Doctrine contradicts across books\n"
            "– Cannot reconcile authoritative views\n"
            "– Situation is genuinely ambiguous\n\n"
            "RECOMMENDED POSTURE:\n"
            "– Hold position\n"
            "– Gather more data\n"
            "– Avoid forced choice"
        ),
    }

    @staticmethod
    def frame_silence(
        reason: str = "insufficient_doctrine",
        confidence: float = 0.3,
    ) -> str:
        """
        Frame silence as an action.
        
        Args:
            reason: key in SILENCE_TEMPLATES
            confidence: how confident we are in silence
        
        Returns:
            formatted silence text
        """
        template = SilenceManager.SILENCE_TEMPLATES.get(
            reason, SilenceManager.SILENCE_TEMPLATES["insufficient_doctrine"]
        )
        
        return f"{template}\n\nCONFIDENCE IN SILENCE: {confidence:.0%}"

    @staticmethod
    def log_silence(
        query: str,
        reason: str,
        confidence: float,
        timestamp: str = "",
    ) -> Dict[str, Any]:
        """
        Create a silence log entry (immutable record).
        
        Returns:
            dict suitable for JSON serialization
        """
        return {
            "type": "SILENCE",
            "query": query,
            "reason": reason,
            "confidence": confidence,
            "timestamp": timestamp,
        }


class PrimeConfidant:
    """
    N — Sovereign's most trusted advisor.
    Role: compress outcomes, surface risks, expose uncertainty, frame silence clearly.
    
    N is allowed to:
    – downgrade confidence
    – highlight ignored risks
    – restate Tribunal verdict
    
    N is NOT allowed to:
    – override Tribunal
    – invent advice
    – break silence
    """

    def frame_verdict(
        self,
        tribunal_verdict: str,
        minister_outputs: List[Dict[str, Any]],
        silence_text: str = "",
        query: str = "",
    ) -> str:
        """
        Frame final output based on Tribunal verdict.
        
        Returns ONE OF:
        1. Advice shape (if ALLOW)
        2. Silence shape (if SILENCE)
        3. Escalation shape (if ESCALATE)
        """
        if tribunal_verdict == "ALLOW":
            return self._frame_advice(minister_outputs)
        elif tribunal_verdict == "SILENCE":
            return self._frame_silence(silence_text)
        elif tribunal_verdict == "ESCALATE":
            return self._frame_escalation()
        else:
            return self._frame_silence(
                SilenceManager.frame_silence("insufficient_doctrine", 0.2)
            )

    def _frame_advice(self, minister_outputs: List[Dict[str, Any]]) -> str:
        """Frame advice-allowed output."""
        lines = [
            "=" * 60,
            "RECOMMENDED PATH",
            "=" * 60,
            "",
        ]

        for m in minister_outputs[:3]:  # Show top 3 ministers
            lines.append(f"{m.get('minister', 'Unknown').upper()}")
            lines.append(f"Position: {m.get('position', '')}")
            lines.append(f"Confidence: {m.get('confidence', 0.0):.0%}")
            
            if m.get("risk_flags"):
                lines.append(f"Risks: {', '.join(m.get('risk_flags', []))}")
            
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _frame_silence(self, silence_text: str) -> str:
        """Frame silence output."""
        return f"\n{silence_text}\n"

    def _frame_escalation(self) -> str:
        """Frame escalation output."""
        return (
            "ESCALATION REQUIRED\n\n"
            "WHY:\n"
            "– Contradictory doctrine\n"
            "– High irreversible risk\n"
            "– Ethical ambiguity\n\n"
            "NO ADVICE GIVEN.\n"
        )
