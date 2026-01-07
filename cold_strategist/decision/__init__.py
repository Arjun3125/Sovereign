"""
Decision Engine: Structured decision analysis and enforcement

Phases:
- Phase-1: Strategic situation analysis (phase1_analyzer.py)
  - Analyzes situations using LLM
  - Produces structured Phase1Response
  - Validates decision output
  
- Phase-3: Decision enforcement & escalation (phase3_enforcer.py)
  - Executes approved decisions
  - Manages escalations
  - Tracks execution status
"""

from .phase1_analyzer import (
    Phase1Response,
    Decision,
    ActionItem,
    analyze_situation,
    call_llm,
    validate_response,
    PROMPT,
    EXAMPLES,
    run_demo as demo_phase1,
)

from .phase3_enforcer import (
    Phase3Enforcer,
    ExecutionResult,
    get_enforcer,
)

__all__ = [
    # Phase-1
    "Phase1Response",
    "Decision",
    "ActionItem",
    "analyze_situation",
    "call_llm",
    "validate_response",
    "PROMPT",
    "EXAMPLES",
    "demo_phase1",
    
    # Phase-3
    "Phase3Enforcer",
    "ExecutionResult",
    "get_enforcer",
]
