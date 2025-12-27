"""
Input Prompts - Collect Context and State from User

Builds Context and State objects from CLI args and interactive input.
"""

from typing import Tuple


class Context:
    """Wrapper for decision context (will integrate with core.contracts.context)."""
    
    def __init__(self, raw_text: str, domain: str, stakes: str, emotional_load: float, reversibility: str = None):
        self.raw_text = raw_text
        self.domain = domain
        self.stakes = stakes
        self.emotional_load = emotional_load
        # Use provided reversibility, or infer from stakes
        self.reversibility = reversibility or ("reversible" if stakes in ["low", "medium"] else "irreversible")
        self.compounding = stakes in ["high", "existential"]
        self.memory = None  # Placeholder for memory context


class State:
    """Wrapper for decision state (will integrate with core.contracts.state)."""
    
    def __init__(self, emotional_load: float, urgency: float, fatigue: float, stakes: str):
        self.emotional_load = emotional_load
        self.urgency = urgency
        self.fatigue = fatigue
        self.stakes = stakes
        self.time_pressure = urgency  # Alias for consistency
        self.resources = max(0.0, 1.0 - fatigue)  # Inverse: fatigue → resource depletion


def collect_context(args) -> Tuple[Context, State]:
    """
    Collect context and state from CLI args and user input.
    
    Args:
        args: Parsed arguments from argparse
        
    Returns:
        Tuple of (Context, State)
    """
    # Prompt user for situation description
    print("\n" + "="*70)
    print(f"MODE: {args.mode.upper()} | DOMAIN: {args.domain.upper()}")
    print("="*70)
    
    raw_text = input("\nDescribe the situation:\n> ").strip()
    
    if not raw_text:
        raise ValueError("Situation description required")
    
    # Build Context
    context = Context(
        raw_text=raw_text,
        domain=args.domain,
        stakes=args.stakes,
        emotional_load=args.emotional_load,
        reversibility=getattr(args, 'reversibility', None)  # Use CLI arg if provided
    )
    
    # Build State
    state = State(
        emotional_load=args.emotional_load,
        urgency=args.urgency,
        fatigue=args.fatigue,
        stakes=args.stakes
    )
    
    # Add war-specific context if applicable
    if args.mode == "war":
        context.arena = args.arena
        context.constraints = args.constraints
        state.opponent_hostility = 0.5  # Default; can be refined by LLM later
    
    return context, state


def collect_outcome(event_id: str) -> dict:
    """
    Collect outcome information for a previously logged event.
    
    Args:
        event_id: The event ID to resolve
        
    Returns:
        Outcome dict with result, damage, benefit, lessons
    """
    print("\n" + "="*70)
    print(f"RESOLVE OUTCOME FOR EVENT: {event_id}")
    print("="*70)
    
    print("\nOutcome result (success | partial | failure):")
    result = input("> ").strip().lower()
    
    if result not in ["success", "partial", "failure"]:
        result = "partial"  # Default
    
    print("Actual damage incurred (0.0-1.0):")
    try:
        damage = float(input("> "))
        damage = max(0.0, min(1.0, damage))
    except ValueError:
        damage = 0.0
    
    print("Benefit gained (0.0-1.0):")
    try:
        benefit = float(input("> "))
        benefit = max(0.0, min(1.0, benefit))
    except ValueError:
        benefit = 0.0
    
    print("Lessons learned (comma-separated, or press Enter to skip):")
    lessons_str = input("> ").strip()
    lessons = [l.strip() for l in lessons_str.split(",") if l.strip()] if lessons_str else []
    
    return {
        "result": result,
        "damage": damage,
        "benefit": benefit,
        "lessons": lessons
    }
