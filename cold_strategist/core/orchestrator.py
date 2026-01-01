"""
Orchestrator - High-level Coordination
Coordinates between all system components.

Integrates Phase-1 (initial assessment) → Phase-3 (pipeline routing).
"""

from typing import Optional, Tuple, Literal
from cold_strategist.phase1.llm_client import call_llm
from cold_strategist.phase1.phase1_prompt import PROMPT, validate_response
from cold_strategist.phase1.schema import Phase1Response
from cold_strategist.phase3 import Phase3Assessment, Phase3Evaluator, apply_phase3_routing


class Orchestrator:
    """High-level coordinator of the entire Sovereign system.
    
    Pipeline:
    1. Phase-1: Initial assessment of situation (sufficient context?)
    2. Phase-3: Evaluate Phase-1 output and decide routing (proceed inline, escalate, request more info)
    3. Route to Quick/Normal/War mode based on Phase-3 decision
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.phase3_evaluator = Phase3Evaluator()

    def coordinate(self):
        """Coordinate system components."""
        pass

    def get_initial_assessment(self, situation: str) -> Optional[Phase1Response]:
        """Get Phase-1 initial assessment of a situation.

        Args:
            situation: Description of the situation to assess

        Returns:
            Phase1Response object if successful, None on failure

        Raises:
            ValueError: if LLM is not configured or response is invalid
        """
        if not situation or not situation.strip():
            raise ValueError("Situation cannot be empty")

        full_prompt = PROMPT + "\n\nSITUATION:\n" + situation + "\n\nRespond with a single JSON object."

        try:
            raw = call_llm(full_prompt)
            resp = validate_response(raw)
            return resp
        except Exception as e:
            # Log and re-raise; caller decides how to handle
            raise

    def assess_and_route(
        self, situation: str
    ) -> Tuple[Phase1Response, Phase3Assessment, Optional[Literal["quick", "normal", "war"]]]:
        """Run Phase-1 assessment and Phase-3 routing decision.
        
        Full pipeline:
        1. Phase-1 LLM assesses situation
        2. Phase-3 evaluator decides routing
        3. Returns both responses + recommended mode
        
        Args:
            situation: Description of the situation
            
        Returns:
            Tuple of (Phase1Response, Phase3Assessment, mode_override)
            mode_override: "quick", "normal", "war", or None if needs more info
            
        Raises:
            ValueError: if situation is empty or LLM call fails
        """
        # Phase-1: Initial assessment
        phase1_resp = self.get_initial_assessment(situation)
        
        # Phase-3: Routing decision
        phase3_assessment, mode_override = apply_phase3_routing(
            phase1_resp,
            evaluator=self.phase3_evaluator
        )
        
        return phase1_resp, phase3_assessment, mode_override
