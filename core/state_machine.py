"""
Darbar State Machine - Canonical State Flow (LOCKED)

Enforces strict disciplinary control over conversation flow.
No state can be entered unless explicitly allowed.
Ministers, LLM, N, and Memory operations are gated by state.
"""

from enum import Enum, auto
from typing import List, Tuple


# ============================================================================
# CANONICAL STATES (LOCKED)
# ============================================================================

class DarbarState(Enum):
    """Canonical states for the Darbar decision-making process."""
    IDLE = auto()
    CONTEXT_BUILDING = auto()
    CONTEXT_VALIDATION = auto()
    MINISTER_SELECTION = auto()
    DEBATE = auto()
    QUICK_PATH = auto()
    VERDICT_SYNTHESIS = auto()
    SOVEREIGN_DECISION = auto()
    MEMORY_COMMIT = auto()
    TERMINATED = auto()


# ============================================================================
# ALLOWED TRANSITIONS (STRICT)
# ============================================================================

ALLOWED_TRANSITIONS = {
    DarbarState.IDLE: [
        DarbarState.CONTEXT_BUILDING
    ],

    DarbarState.CONTEXT_BUILDING: [
        DarbarState.CONTEXT_VALIDATION
    ],

    DarbarState.CONTEXT_VALIDATION: [
        DarbarState.MINISTER_SELECTION,
        DarbarState.CONTEXT_BUILDING,  # if info insufficient
    ],

    DarbarState.MINISTER_SELECTION: [
        DarbarState.DEBATE,
        DarbarState.QUICK_PATH
    ],

    DarbarState.DEBATE: [
        DarbarState.VERDICT_SYNTHESIS
    ],

    DarbarState.QUICK_PATH: [
        DarbarState.VERDICT_SYNTHESIS
    ],

    DarbarState.VERDICT_SYNTHESIS: [
        DarbarState.SOVEREIGN_DECISION
    ],

    DarbarState.SOVEREIGN_DECISION: [
        DarbarState.MEMORY_COMMIT,
        DarbarState.DEBATE,  # override-triggered re-evaluation
    ],

    DarbarState.MEMORY_COMMIT: [
        DarbarState.IDLE
    ],

    DarbarState.TERMINATED: []  # Terminal state
}


# ============================================================================
# STATE MACHINE CLASS (Minimal, Clean)
# ============================================================================

class DarbarStateMachine:
    """
    Enforces strict state transitions in Darbar.
    
    No other transitions are legal.
    Anything else → RuntimeError exception.
    """

    def __init__(self):
        self.state: DarbarState = DarbarState.IDLE
        self.history: List[Tuple[DarbarState, DarbarState]] = []

    def transition(self, next_state: DarbarState) -> None:
        """
        Attempt to transition to next_state.
        
        Args:
            next_state: The target state.
            
        Raises:
            RuntimeError: If transition is not in ALLOWED_TRANSITIONS.
        """
        if next_state not in ALLOWED_TRANSITIONS[self.state]:
            raise RuntimeError(
                f"Illegal transition: {self.state.name} → {next_state.name}"
            )

        self.history.append((self.state, next_state))
        self.state = next_state

    def current(self) -> DarbarState:
        """Return the current state."""
        return self.state

    def get_history(self) -> List[Tuple[DarbarState, DarbarState]]:
        """Return the full transition history."""
        return self.history.copy()


# ============================================================================
# ENFORCEMENT RULES (IMPORTANT)
# ============================================================================

"""
ENFORCEMENT RULES (Code-based discipline, not trust):

1. Ministers cannot speak unless state >= MINISTER_SELECTION
   - Minister.speak() should check: self.sm.current() >= DarbarState.MINISTER_SELECTION

2. Debate cannot occur unless state == DEBATE
   - DebateEngine.debate() should check: self.sm.current() == DarbarState.DEBATE

3. LLM cannot ask questions unless state == CONTEXT_BUILDING
   - LLMInterface.ask() should check: self.sm.current() == DarbarState.CONTEXT_BUILDING

4. N cannot synthesize unless state == VERDICT_SYNTHESIS
   - N.synthesize() should check: self.sm.current() == DarbarState.VERDICT_SYNTHESIS

5. Memory is append-only and only allowed in MEMORY_COMMIT
   - EventStore.append() should check: self.sm.current() == DarbarState.MEMORY_COMMIT
   - OutcomeStore.append() should check: self.sm.current() == DarbarState.MEMORY_COMMIT
   - PatternStore.append() should check: self.sm.current() == DarbarState.MEMORY_COMMIT
"""


# ============================================================================
# EXAMPLE FLOW (Live Decision)
# ============================================================================

def example_flow():
    """
    Demonstrates a complete canonical flow through the state machine.
    """
    sm = DarbarStateMachine()

    # Full happy path
    sm.transition(DarbarState.CONTEXT_BUILDING)
    sm.transition(DarbarState.CONTEXT_VALIDATION)
    sm.transition(DarbarState.MINISTER_SELECTION)
    sm.transition(DarbarState.DEBATE)
    sm.transition(DarbarState.VERDICT_SYNTHESIS)
    sm.transition(DarbarState.SOVEREIGN_DECISION)
    sm.transition(DarbarState.MEMORY_COMMIT)
    sm.transition(DarbarState.IDLE)

    print("Flow completed successfully.")
    print(f"Final state: {sm.current().name}")
    print(f"Transition history: {[(s1.name, s2.name) for s1, s2 in sm.get_history()]}")


if __name__ == "__main__":
    example_flow()
