"""
Debate Engine - Minister Deliberation Orchestration (LOCKED)

Manages the complete debate flow:

Phase 1: Independent Positions
- Each minister submits verdict without knowledge of others
- All verdicts validated against contention rules

Phase 2: Objection & Response
- Ministers object to each other (specific types only)
- Original verdicts stand; objections are recorded

Phase 3: Concessions (Optional)
- Ministers can revise claims based on valid objections
- Not consensus, but acknowledgment of partial truth

Output: Clean JSON package for N synthesis
- Verdicts (all positions)
- Objections (all challenges)
- Concessions (all revisions)
- Contradictions (structural conflicts detected)
- Dominant risks (consensus warnings)
"""

from typing import List, Optional, Dict, Tuple
from context.context_schema import DecisionContext
from core.debate.debate_schema import (
    MinisterVerdict,
    Objection,
    Concession,
    DebateRound,
    ObjectionType,
    VerdictType
)
from core.debate.contention_rules import ContentionRules
from core.debate.speaking_order import SpeakingOrder
from core.debate.contradiction_detector import ContradictionDetector, Contradiction
from core.debate.verdict_formatter import VerdictFormatter


class DebateEngine:
    """
    Orchestrates minister debate.
    
    Ensures:
    - Phase separation (no influence between phases)
    - Rule enforcement (no ethical language, no repetition, etc.)
    - Contradiction detection (structural conflicts surfaced)
    - Clean output for N (no noise, all essentials)
    """
    
    def __init__(self):
        """Initialize debate engine with rules and detectors."""
        self.contention_rules = ContentionRules()
        self.contradiction_detector = ContradictionDetector()
        self.formatter = VerdictFormatter()
        self.current_round: Optional[DebateRound] = None
    
    def conduct_debate(
        self,
        ctx: DecisionContext,
        selected_ministers: List[Tuple[str, int]]
    ) -> Dict:
        """
        Conduct complete debate and return formatted output for N.
        
        Args:
            ctx: Decision context
            selected_ministers: List of (minister_name, score) tuples
            
        Returns:
            Formatted debate output dict
        """
        # Generate speaking order
        speaking_order = SpeakingOrder.generate(selected_ministers)
        
        # Phase 1: Independent Positions
        self.current_round = DebateRound(phase=1)
        verdicts = self._phase1_independent_positions(speaking_order)
        self.current_round.verdicts = verdicts
        
        # Phase 2: Objection & Response
        objections = self._phase2_objections(verdicts, speaking_order)
        self.current_round.objections = objections
        
        # Phase 3: Concessions (optional)
        concessions = self._phase3_concessions(verdicts, objections)
        self.current_round.concessions = concessions
        
        # Detect contradictions
        contradictions = self.contradiction_detector.detect_all(verdicts)
        
        # Extract dominant risks
        dominant_risks = self._extract_dominant_risks(verdicts)
        
        # Find least-damage path (if exists)
        least_damage_path = self._find_least_damage_path(verdicts)
        
        # Format output for N
        output = self.formatter.format_debate_output(
            self.current_round,
            contradictions,
            dominant_risks,
            least_damage_path
        )
        
        return output
    
    def _phase1_independent_positions(self, speaking_order: List[str]) -> List[MinisterVerdict]:
        """
        Phase 1: Each minister submits independent verdict.
        
        No knowledge of other verdicts. No influence. Pure position.
        
        Args:
            speaking_order: Order ministers speak (determines presentation sequence)
            
        Returns:
            List of MinisterVerdict objects (one per minister)
        """
        verdicts = []
        
        # In real implementation, this would call out to minister analysis
        # For now, structure shows where verdicts come from
        
        for minister_name in speaking_order:
            # This would be LLM call to actual minister analysis
            # verdict = self._get_minister_verdict(minister_name)
            
            # For structure, create placeholder
            verdict = MinisterVerdict(
                minister_name=minister_name,
                position="[Position to be filled by minister analysis]",
                warning="[Warning to be filled by minister analysis]",
                confidence=0.0,
                verdict_type=VerdictType.CONTINGENT
            )
            
            # Validate against contention rules
            is_valid, violations = self.contention_rules.validate_verdict(verdict)
            
            if not is_valid:
                # In real system: return violations to minister for revision
                pass
            else:
                verdicts.append(verdict)
        
        return verdicts
    
    def _phase2_objections(
        self,
        verdicts: List[MinisterVerdict],
        speaking_order: List[str]
    ) -> List[Objection]:
        """
        Phase 2: Ministers object to each other's verdicts.
        
        After seeing all Phase 1 verdicts, each minister can file objections.
        Objections are validated; violations sent back for revision.
        
        Args:
            verdicts: Verdicts from Phase 1
            speaking_order: Original speaking order (used for timing)
            
        Returns:
            List of valid Objection objects
        """
        objections = []
        verdicts_by_minister = {v.minister_name: v for v in verdicts}
        
        # Each minister can object to others
        for objector in speaking_order:
            # In real system: call minister to generate objections
            # proposed_objections = self._get_minister_objections(objector, verdicts)
            
            # For structure, placeholder
            proposed_objections = []
            
            # Validate each objection
            for obj in proposed_objections:
                is_valid, violations = self.contention_rules.validate_objection(
                    obj,
                    objections  # Prior objections to check for repetition
                )
                
                if not is_valid:
                    # Return violations to minister for revision
                    pass
                else:
                    objections.append(obj)
        
        return objections
    
    def _phase3_concessions(
        self,
        verdicts: List[MinisterVerdict],
        objections: List[Objection]
    ) -> List[Concession]:
        """
        Phase 3: Ministers can concede partial validity of objections.
        
        NOT consensus. NOT agreement. But acknowledgment of partial truth
        or scope limitations.
        
        Args:
            verdicts: Phase 1 verdicts (unchanged)
            objections: Objections from Phase 2
            
        Returns:
            List of Concession objects
        """
        concessions = []
        
        # For each minister, check if they want to concede anything
        for verdict in verdicts:
            # Get objections aimed at this minister
            objections_to_me = [
                o for o in objections
                if o.target_minister == verdict.minister_name
            ]
            
            # In real system: ask minister which (if any) they concede to
            # conceded = self._get_minister_concessions(verdict.minister_name, objections_to_me)
            
            # For structure, placeholder
            conceded = []
            concessions.extend(conceded)
        
        return concessions
    
    def _extract_dominant_risks(self, verdicts: List[MinisterVerdict]) -> List[str]:
        """
        Extract the most frequently/strongly stated warnings.
        
        Args:
            verdicts: All verdicts
            
        Returns:
            List of top warning themes
        """
        warnings = []
        
        for v in verdicts:
            if v.warning:
                warnings.append(v.warning)
        
        # In real system: cluster and rank by frequency + confidence
        # For structure, return all unique
        return list(set(warnings))
    
    def _find_least_damage_path(self, verdicts: List[MinisterVerdict]) -> Optional[str]:
        """
        If consensus exists on what NOT to do, describe the minimum-harm alternative.
        
        Args:
            verdicts: All verdicts
            
        Returns:
            Description of least-damage path, or None if no consensus
        """
        # In real system: analyze conditions and find overlapping safety bounds
        # For structure, return None
        return None
