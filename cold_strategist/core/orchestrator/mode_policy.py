"""
Mode Policy - Strategy for Execution Mode Selection

Quick Mode is not a separate engine; it is a strategy flag that adjusts
how the orchestrator executes analysis.

This module determines whether to honor a "quick" request or escalate to
"normal" or "war" based on state and memory.

Hard rules:
- Quick Mode never debates (1-shot synthesis only)
- Quick Mode uses only 3 ministers: Truth, Optionality, Domain-specific
- Quick Mode always logs to memory
- If Quick advice is repeatedly overridden → auto-disable for domain
"""

from typing import Optional, Dict, Any


def resolve_execution_mode(
    requested_mode: str,
    state: Optional[Any] = None,
    memory_flags: Optional[Dict[str, Any]] = None,
    domain: Optional[str] = None
) -> str:
    """
    Determine actual execution mode based on request, state, and memory.
    
    Args:
        requested_mode: "quick", "normal", or "war" (user request)
        state: Current state object (emotional_load, stakes, fatigue, urgency)
        memory_flags: Memory-derived signals (e.g., repeat_failure, override_count)
        domain: Current domain (for pattern-based escalation)
        
    Returns:
        Actual execution mode to use: "quick", "normal", or "war"
    """
    # If not requesting quick, return as-is
    if requested_mode != "quick":
        return requested_mode
    
    # Initialize defaults
    if state is None:
        state = type('State', (), {
            'stakes': 'medium',
            'emotional_load': 0.3,
            'fatigue': 0.3,
            'urgency': 0.3
        })()
    
    if memory_flags is None:
        memory_flags = {}
    
    # Hard escalation rules for Quick Mode
    
    # Rule 1: High stakes always escalate to normal
    if getattr(state, 'stakes', None) == 'high' or getattr(state, 'stakes', None) == 'existential':
        return 'normal'
    
    # Rule 2: High emotional load escalates to normal
    if getattr(state, 'emotional_load', 0.3) > 0.6:
        return 'normal'
    
    # Rule 3: High urgency or fatigue escalates to normal
    if getattr(state, 'urgency', 0.3) > 0.7 or getattr(state, 'fatigue', 0.3) > 0.7:
        return 'normal'
    
    # Rule 4: Repeated failures in domain disable quick mode
    if memory_flags.get('quick_mode_disabled_for_domain', False):
        return 'normal'
    
    # Rule 5: If quick mode was overridden more than 2x recently, escalate
    recent_overrides = memory_flags.get('recent_quick_overrides', 0)
    if recent_overrides >= 3:
        return 'normal'
    
    # Rule 6: If pattern detected as sensitive/recurring, escalate
    if memory_flags.get('repeat_failure'):
        return 'normal'
    
    if memory_flags.get('sensitive_pattern'):
        return 'normal'
    
    # No escalation needed—use quick mode
    return 'quick'


def get_quick_ministers() -> list:
    """
    Get the fixed set of ministers for Quick Mode.
    
    Returns:
        List of minister names: ["Truth", "Optionality", "<domain_minister>"]
    """
    # Note: domain_minister is added dynamically based on context.domain
    return ["Truth", "Optionality"]


def should_disable_quick_for_domain(
    domain: str,
    memory_flags: Dict[str, Any]
) -> bool:
    """
    Check if Quick Mode should be permanently disabled for a domain.
    
    Quick Mode is auto-disabled if advice is repeatedly overridden
    (threshold: 3+ overrides in recent memory).
    
    Args:
        domain: The decision domain
        memory_flags: Memory-derived signals
        
    Returns:
        True if Quick Mode should be disabled for this domain
    """
    override_count = memory_flags.get(f'quick_overrides_in_{domain}', 0)
    return override_count >= 3


def quick_mode_summary(
    domain: str,
    memory_flags: Dict[str, Any]
) -> str:
    """
    Generate summary of Quick Mode status for a domain.
    
    Args:
        domain: The decision domain
        memory_flags: Memory-derived signals
        
    Returns:
        Human-readable summary
    """
    override_count = memory_flags.get(f'quick_overrides_in_{domain}', 0)
    is_disabled = should_disable_quick_for_domain(domain, memory_flags)
    
    status = "DISABLED" if is_disabled else "ENABLED"
    
    return f"Quick Mode ({domain}): {status} | {override_count} recent overrides"
