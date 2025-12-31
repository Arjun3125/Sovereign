"""
Main - Cold Strategist CLI Entry Point

Usage:
    cold normal --domain career --stakes high
    cold war --domain negotiation --stakes medium --arena career
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cli.args import parse_args, validate_args
from cli.prompts import collect_context, collect_outcome
from cli.render import render_verdict, render_patterns, render_calibration, render_learning_summary, render_error
from core.orchestrator.engine import run_analysis, resolve_outcome, get_learning_summary


def main():
    """Main entry point for Cold Strategist CLI."""
    try:
        # Parse and validate arguments
        args = parse_args()
        validate_args(args)
        
        # Collect context and state from user
        context, state = collect_context(args)
        
        # Run analysis
        result = run_analysis(
            mode=args.mode,
            context=context,
            state=state,
            log_to_memory=args.log_memory,
            analyze_patterns=args.analyze_patterns
        )
        
        # Render verdict
        render_verdict(result["verdict"])
        
        # Render patterns if detected
        if result.get("patterns"):
            render_patterns(result["patterns"])
        
        # Render calibration if available
        if result.get("calibration"):
            render_calibration(result["calibration"])
        
        # Optionally show learning summary
        if args.analyze_patterns:
            summary = get_learning_summary(args.mode)
            if summary:
                render_learning_summary(summary)
        
        # Save event ID for later outcome resolution
        if result.get("event_id"):
            print("\n" + "="*70)
            print("EVENT LOGGED")
            print("="*70)
            print(f"\nEvent ID: {result['event_id']}")
            print("Use this ID to log outcome later:")
            print(f"  cold-outcome {result['event_id']} --mode {args.mode}")
            print()
    
    except KeyboardInterrupt:
        print("\n\nCancelled.\n")
        sys.exit(0)
    
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


def outcome_main():
    """Entry point for resolving outcomes."""
    try:
        import argparse
        
        parser = argparse.ArgumentParser(prog="cold-outcome")
        parser.add_argument("event_id", help="Event ID to resolve")
        parser.add_argument(
            "--mode",
            choices=["normal", "war"],
            default="war",
            help="Analysis mode"
        )
        
        args = parser.parse_args()
        
        # Collect outcome
        outcome = collect_outcome(args.event_id)
        
        # Resolve it
        result = resolve_outcome(args.event_id, outcome, mode=args.mode)
        
        print("\n" + "="*70)
        print("OUTCOME RESOLVED")
        print("="*70)
        print(f"\nEvent ID: {result['event_id']}")
        print(f"Outcome: {result.get('outcome', 'unknown')}")
        print(f"Damage: {result.get('outcome_damage', 0.0):.2f}")
        print(f"Benefit: {result.get('outcome_benefit', 0.0):.2f}")
        print()
        
        # Show updated learning
        summary = get_learning_summary(args.mode)
        if summary:
            render_learning_summary(summary)
    
    except KeyboardInterrupt:
        print("\n\nCancelled.\n")
        sys.exit(0)
    
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    # Determine which entry point was called
    if "outcome" in sys.argv[0]:
        outcome_main()
    else:
        main()
