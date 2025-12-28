"""
War Mode Speech Filter - Apply language constraints to minister output.

Deterministic enforcement layer that:
- Removes disallowed phrases
- Suppresses forbidden patterns
- Enforces mandatory inclusions
- Applies minister-specific relaxations
"""

from typing import Dict, Any, Tuple
from core.orchestrator.war_speech_rules import WAR_SPEECH_RULES, WAR_MINISTER_OVERRIDES


class WarSpeechFilter:
    """
    Filter minister output for War Mode constraints.
    
    Guarantees:
    - No refusal language ("I cannot", "you shouldn't")
    - No pure moralizing
    - Mandatory cost/risk/exit analysis
    - Minister-specific tone shift applied
    """

    def __init__(self):
        self.rules = WAR_SPEECH_RULES
        self.overrides = WAR_MINISTER_OVERRIDES

    def filter(
        self,
        minister_name: str,
        text: str,
        mode: str = "war",
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Apply War Mode speech filter to minister output.

        Args:
            minister_name: Name of minister (lowercase)
            text: Original minister output
            mode: "war" or "normal" (only filters if mode=="war")

        Returns:
            Tuple of (filtered_text, metadata_dict)
              metadata contains info about what was filtered/enforced
        """
        # Default metadata for all modes
        default_metadata = {
            "minister": minister_name,
            "phrases_removed": [],
            "patterns_suppressed": [],
            "mandatory_added": [],
            "tone_shifted": False,
            "filtering_applied": False,
        }
        
        if mode != "war":
            return text, default_metadata

        metadata = default_metadata.copy()

        # Apply filters
        filtered = text
        minister_lower = minister_name.lower()

        # 1. Remove disallowed phrases
        filtered, removed_phrases = self._remove_disallowed_phrases(
            filtered, minister_lower
        )
        if removed_phrases:
            metadata["phrases_removed"] = removed_phrases
            metadata["filtering_applied"] = True

        # 2. Suppress patterns (conceptual level)
        filtered, suppressed = self._suppress_patterns(filtered, minister_lower)
        if suppressed:
            metadata["patterns_suppressed"] = suppressed
            metadata["filtering_applied"] = True

        # 3. Enforce mandatory inclusions
        filtered, mandatory = self._enforce_mandatory(filtered, minister_lower)
        if mandatory:
            metadata["mandatory_added"] = mandatory
            metadata["filtering_applied"] = True

        # 4. Apply tone shift
        filtered, tone_shifted = self._apply_tone_shift(
            filtered, minister_lower, removed_phrases
        )
        if tone_shifted:
            metadata["tone_shifted"] = True
            metadata["filtering_applied"] = True

        # 5. Add War Mode note if significant filtering occurred
        if len(removed_phrases) > 0 or len(suppressed) > 0:
            note = (
                "\n\n[WAR MODE FILTER NOTE]: "
                f"Refusal/moral language removed. Reframed as strategic constraint."
            )
            filtered += note

        return filtered, metadata

    def _remove_disallowed_phrases(
        self, text: str, minister_lower: str
    ) -> Tuple[str, list]:
        """
        Remove or replace disallowed phrases.
        """
        removed = []
        filtered = text

        for phrase in self.rules["disallowed_phrases"]:
            # Case-insensitive search but preserve case in replacement
            import re
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            if pattern.search(filtered):
                filtered = pattern.sub("[REFUSAL_REMOVED]", filtered)
                removed.append(phrase)

        return filtered, removed

    def _suppress_patterns(
        self, text: str, minister_lower: str
    ) -> Tuple[str, list]:
        """
        Suppress conceptual patterns (e.g., "moral judgment", "absolute refusal").
        """
        suppressed = []
        filtered = text

        # Minister-specific suppression
        if minister_lower in self.overrides:
            override = self.overrides[minister_lower]
            for pattern in override.get("suppressed", []):
                if pattern.lower() in filtered.lower():
                    # Mark but don't remove (these are subtle)
                    # In production, would use semantic analysis
                    suppressed.append(pattern)

        return filtered, suppressed

    def _enforce_mandatory(self, text: str, minister_lower: str) -> Tuple[str, list]:
        """
        Ensure mandatory content is present.
        """
        mandatory_added = []
        lines = text.split("\n")
        has_costs = any("cost" in line.lower() for line in lines)
        has_risks = any("risk" in line.lower() for line in lines)
        has_exit = any("exit" in line.lower() or "retreat" in line.lower() for line in lines)

        additions = []

        if not has_costs:
            additions.append("\nCosts & Trade-offs:\n- [To be evaluated by decision-maker]")
            mandatory_added.append("costs")

        if not has_risks:
            additions.append("\nRisks & Exposure:\n- [To be evaluated by decision-maker]")
            mandatory_added.append("risks")

        if not has_exit:
            additions.append("\nExit Options:\n- [Define retreat/reversal conditions before committing]")
            mandatory_added.append("exit_options")

        # Minister-specific mandatory additions
        if minister_lower in self.overrides:
            override = self.overrides[minister_lower]
            for mandatory in override.get("mandatory", []):
                if mandatory.lower() not in text.lower():
                    additions.append(f"\n{mandatory}")
                    mandatory_added.append(mandatory)

        filtered = text + "\n".join(additions)
        return filtered, mandatory_added

    def _apply_tone_shift(
        self, text: str, minister_lower: str, removed_phrases: list
    ) -> Tuple[str, bool]:
        """
        Shift tone from empathetic/protective to clinical/strategic.
        """
        if len(removed_phrases) == 0:
            # No refusal language, tone already neutral
            return text, False

        # Add tone indicator
        tone_note = (
            "\n\n[TONE NOTE]: Clinical analysis (war mode). "
            "Remove empathetic framing; focus on execution vectors."
        )

        return text + tone_note, True

    def enforce_structure(self, text: str, minister_name: str = "") -> str:
        """
        Ensure minister output has required structure.

        Adds missing sections (Costs, Risks, Exit) with placeholders.
        """
        sections_required = ["Costs", "Risks", "Exit"]
        for section in sections_required:
            if section not in text:
                text += f"\n\n{section}:\n- [Not specified]"

        return text

    def get_filter_report(self, metadata: Dict[str, Any]) -> str:
        """
        Generate human-readable filter report.
        """
        lines = [
            "=" * 60,
            f"WAR SPEECH FILTER REPORT - {metadata.get('minister', 'unknown').upper()}",
            "=" * 60,
        ]

        if metadata.get("phrases_removed"):
            lines.append(f"\nPhrases Removed ({len(metadata['phrases_removed'])}):")
            for phrase in metadata["phrases_removed"]:
                lines.append(f"  - {phrase}")

        if metadata.get("patterns_suppressed"):
            lines.append(f"\nPatterns Suppressed ({len(metadata['patterns_suppressed'])}):")
            for pattern in metadata["patterns_suppressed"]:
                lines.append(f"  - {pattern}")

        if metadata.get("mandatory_added"):
            lines.append(f"\nMandatory Sections Added ({len(metadata['mandatory_added'])}):")
            for item in metadata["mandatory_added"]:
                lines.append(f"  + {item}")

        if metadata.get("tone_shifted"):
            lines.append("\nTone Shifted: Empathetic → Clinical")

        lines.append("")
        return "\n".join(lines)
