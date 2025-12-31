"""
War Mode Debate Wrapper
Integrates speech filters into debate proceedings for War Mode

When War Mode is active:
1. Debate proceeds normally (all ministers retrieved, synthesized, debated)
2. All advice goes through WarSpeechFilter before finalization
3. Filtered advice + metadata returned with original for comparison
4. Audit trail tracks all suppressions for transparency
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from debate.knowledge_debate_engine import DebateProceedings, DebatePosition
from core.orchestrator.war_speech_filter import WarSpeechFilter


@dataclass
class WarModeDebateResult:
    """Debate result with War Mode speech filtering applied."""
    original_proceedings: DebateProceedings
    filtered_proceedings: DebateProceedings
    filter_audit: Dict[str, Any]
    suppressions_count: int
    filtering_notes: str
    
    def __post_init__(self):
        """Compute statistics."""
        self.suppressions_count = sum(
            1 for pos in self.filtered_proceedings.positions 
            if pos.advice and pos.advice != self._find_original_advice(pos.minister)
        )
        self.filtering_notes = f"War Mode: {self.suppressions_count} position(s) filtered for speech constraints"
    
    def _find_original_advice(self, minister_name: str) -> Optional[str]:
        """Find original advice for a minister."""
        for pos in self.original_proceedings.positions:
            if pos.minister == minister_name:
                return pos.advice
        return None


class WarModeDebateWrapper:
    """Applies speech filters to debate proceedings in War Mode."""
    
    def __init__(self):
        """Initialize with speech filter."""
        self.speech_filter = WarSpeechFilter()
    
    def apply_war_mode_filters(
        self,
        proceedings: DebateProceedings,
        mode: str = "war"
    ) -> WarModeDebateResult:
        """
        Apply War Mode speech filters to debate proceedings.
        
        Args:
            proceedings: Original debate proceedings
            mode: "war" to filter, anything else to pass through
        
        Returns:
            WarModeDebateResult with filtered proceedings + audit trail
        """
        if mode != "war":
            # No filtering in non-war modes
            return WarModeDebateResult(
                original_proceedings=proceedings,
                filtered_proceedings=proceedings,
                filter_audit={},
                suppressions_count=0,
                filtering_notes="Normal Mode: No speech filtering applied"
            )
        
        # Filter each position's advice
        filtered_positions: List[DebatePosition] = []
        filter_audit: Dict[str, Any] = {}
        
        for position in proceedings.positions:
            if not position.advice:
                # No advice to filter
                filtered_positions.append(position)
                continue
            
            # Apply filter
            filtered_advice, filter_metadata = self.speech_filter.filter(
                minister_name=position.minister,
                text=position.advice,
                mode="war"
            )
            
            # Track what was filtered
            filter_audit[position.minister] = {
                "original_length": len(position.advice),
                "filtered_length": len(filtered_advice),
                "was_filtered": filtered_advice != position.advice,
                "metadata": filter_metadata,
                "filter_report": self.speech_filter.get_filter_report(filter_metadata)
            }
            
            # Create filtered position
            filtered_position = DebatePosition(
                minister=position.minister,
                status=position.status,
                advice=filtered_advice,
                rationale=position.rationale,  # Rationale not filtered
                confidence=position.confidence,
                citations=position.citations,  # Citations preserved
                risks=position.risks,  # Risk assessments preserved
            )
            filtered_positions.append(filtered_position)
        
        # Create filtered proceedings
        filtered_proceedings = DebateProceedings(
            positions=filtered_positions,
            escalated=proceedings.escalated,
            tribunal_judgment=proceedings.tribunal_judgment,
            final_verdict=proceedings.final_verdict,
            event_id=proceedings.event_id,
        )
        
        return WarModeDebateResult(
            original_proceedings=proceedings,
            filtered_proceedings=filtered_proceedings,
            filter_audit=filter_audit,
            suppressions_count=0,  # Will be computed in __post_init__
            filtering_notes=""  # Will be computed in __post_init__
        )
    
    def format_war_mode_result(self, result: WarModeDebateResult) -> str:
        """
        Format WarModeDebateResult for display.
        
        Shows:
        - Original vs filtered positions (side-by-side where filtered)
        - Audit trail of suppressions
        - Summary statistics
        """
        output = []
        output.append("=" * 70)
        output.append("WAR MODE DEBATE RESULT")
        output.append("=" * 70)
        output.append("")
        
        # Summary
        output.append(result.filtering_notes)
        output.append("")
        
        # Positions (marked where filtered)
        for minister_pos in result.filtered_proceedings.positions:
            orig_pos = next(
                (p for p in result.original_proceedings.positions if p.minister == minister_pos.minister),
                None
            )
            
            audit = result.filter_audit.get(minister_pos.minister, {})
            was_filtered = audit.get("was_filtered", False)
            
            output.append(f"[{minister_pos.minister.upper()}]")
            if was_filtered:
                output.append("  ⚠️  SPEECH FILTERED IN WAR MODE")
                output.append(f"  Original length: {audit.get('original_length', 0)} chars")
                output.append(f"  Filtered length: {audit.get('filtered_length', 0)} chars")
                output.append("")
            
            if minister_pos.advice:
                # Show filtered advice (with note if filtered)
                advice_lines = minister_pos.advice.split('\n')
                for line in advice_lines[:10]:  # First 10 lines
                    output.append(f"  {line}")
                if len(advice_lines) > 10:
                    output.append(f"  ... ({len(advice_lines) - 10} more lines)")
            else:
                output.append("  [No advice provided]")
            
            output.append("")
        
        # Audit trail
        output.append("=" * 70)
        output.append("FILTERING AUDIT TRAIL")
        output.append("=" * 70)
        for minister, audit_data in result.filter_audit.items():
            if audit_data.get("was_filtered"):
                output.append(f"\n{minister.upper()}:")
                report = audit_data.get("filter_report", "")
                if report:
                    for line in report.split('\n'):
                        output.append(f"  {line}")
        
        return "\n".join(output)
