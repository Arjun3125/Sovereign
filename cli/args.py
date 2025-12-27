"""
Argument Parsing - CLI Flags and Options

Defines all command-line arguments for cold strategist.
"""

import argparse


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="cold",
        description="Cold Strategist - Sovereign Counsel Engine"
    )

    # Positional: execution mode
    parser.add_argument(
        "mode",
        choices=["quick", "normal", "war"],
        help="Execution mode: quick (1-shot, no debate), normal (standard counsel), or war (adversarial analysis)"
    )

    # Required: decision domain
    parser.add_argument(
        "--domain",
        required=True,
        choices=["career", "negotiation", "self", "fictional", "other"],
        help="Decision domain"
    )

    # Optional: stakes level
    parser.add_argument(
        "--stakes",
        choices=["low", "medium", "high", "existential"],
        default="medium",
        help="Stakes level (default: medium)"
    )

    # Optional: emotional load (0.0 - 1.0)
    parser.add_argument(
        "--emotional-load",
        type=float,
        default=0.3,
        help="Emotional load factor (0.0-1.0, default: 0.3)"
    )

    # Optional: urgency (0.0 - 1.0)
    parser.add_argument(
        "--urgency",
        type=float,
        default=0.3,
        help="Perceived urgency (0.0-1.0, default: 0.3)"
    )

    # Optional: fatigue (0.0 - 1.0)
    parser.add_argument(
        "--fatigue",
        type=float,
        default=0.3,
        help="Fatigue level (0.0-1.0, default: 0.3)"
    )

    # Optional: war mode specific
    parser.add_argument(
        "--arena",
        choices=["career", "negotiation", "self-discipline", "fictional"],
        help="War mode arena (only for 'war' mode)"
    )

    # Optional: reversibility (for war mode)
    parser.add_argument(
        "--reversibility",
        choices=["reversible", "partially_reversible", "irreversible"],
        default="reversible",
        help="Reversibility of actions (for war mode, default: reversible)"
    )

    # Optional: war mode constraints
    parser.add_argument(
        "--constraints",
        nargs="+",
        default=[],
        help="Constraints for war mode (e.g., reversible minimal_collateral legal)"
    )

    # Optional: enable memory logging
    parser.add_argument(
        "--log-memory",
        action="store_true",
        default=True,
        help="Log decision to memory (default: enabled)"
    )

    # Optional: enable pattern analysis
    parser.add_argument(
        "--analyze-patterns",
        action="store_true",
        default=False,
        help="Analyze recurring patterns after decision"
    )

    return parser.parse_args()


def validate_args(args):
    """Validate argument combinations."""
    # War mode requires arena and reversibility
    if args.mode == "war" and not args.arena:
        raise ValueError("--arena is required for war mode")
    
    if args.mode == "war" and not hasattr(args, 'reversibility'):
        raise ValueError("--reversibility is required for war mode")
    
    # Quick mode doesn't support war-specific options
    if args.mode == "quick" and args.arena:
        raise ValueError("--arena cannot be used with quick mode")
    
    if args.mode == "quick" and args.constraints:
        raise ValueError("--constraints cannot be used with quick mode")

    # Validate numeric ranges
    if args.emotional_load < 0.0 or args.emotional_load > 1.0:
        raise ValueError("--emotional-load must be between 0.0 and 1.0")

    if args.urgency < 0.0 or args.urgency > 1.0:
        raise ValueError("--urgency must be between 0.0 and 1.0")

    if args.fatigue < 0.0 or args.fatigue > 1.0:
        raise ValueError("--fatigue must be between 0.0 and 1.0")

    return True
