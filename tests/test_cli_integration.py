"""
Integration Test: Complete CLI Flow

Tests the end-to-end CLI workflow:
  1. Parse args
  2. Collect context/state
  3. Run analysis (war/normal)
  4. Log to memory
  5. Render verdict
  6. (Later) Resolve outcome
"""

import sys
import os

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cli.args import parse_args, validate_args
from cli.prompts import Context, State
from cli.render import render_verdict, render_patterns
from core.orchestrator.engine import run_analysis, get_learning_summary


def test_cli_war_mode_flow():
    """Test complete war mode CLI flow."""
    
    print("\n" + "="*70)
    print("CLI INTEGRATION TEST: WAR MODE FLOW")
    print("="*70 + "\n")
    
    # Simulate CLI args
    class Args:
        mode = "war"
        domain = "negotiation"
        stakes = "high"
        emotional_load = 0.5
        urgency = 0.6
        fatigue = 0.4
        arena = "career"
        constraints = ["reversible", "minimal_collateral"]
        log_memory = True
        analyze_patterns = True
    
    args = Args()
    
    print("STEP 1: Parse and Validate Args")
    print("-" * 70)
    print(f"✓ Mode: {args.mode}")
    print(f"✓ Domain: {args.domain}")
    print(f"✓ Stakes: {args.stakes}")
    print(f"✓ Arena: {args.arena}")
    print(f"✓ Constraints: {args.constraints}")
    
    # Validate
    try:
        validate_args(args)
        print("✓ Arguments validated")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Simulate context/state collection
    print("\nSTEP 2: Collect Context and State")
    print("-" * 70)
    
    context = Context(
        raw_text="Need to renegotiate unfavorable contract before Q1 ends",
        domain=args.domain,
        stakes=args.stakes,
        emotional_load=args.emotional_load
    )
    context.arena = args.arena
    context.constraints = args.constraints
    
    state = State(
        emotional_load=args.emotional_load,
        urgency=args.urgency,
        fatigue=args.fatigue,
        stakes=args.stakes
    )
    state.opponent_hostility = 0.6
    
    print(f"✓ Context: {context.raw_text[:50]}...")
    print(f"✓ Stakes: {context.stakes}")
    print(f"✓ Emotional load: {state.emotional_load:.1f}")
    print(f"✓ Urgency: {state.urgency:.1f}")
    
    # Run analysis
    print("\nSTEP 3: Run War Mode Analysis")
    print("-" * 70)
    
    try:
        result = run_analysis(
            mode=args.mode,
            context=context,
            state=state,
            log_to_memory=args.log_memory,
            analyze_patterns=args.analyze_patterns
        )
        print(f"✓ Analysis completed")
        print(f"✓ Event ID: {result.get('event_id', 'N/A')[:8]}...")
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Render verdict
    print("\nSTEP 4: Render Verdict")
    print("-" * 70)
    
    if result.get("verdict"):
        render_verdict(result["verdict"])
        print("✓ Verdict rendered")
    
    # Render patterns if available
    print("STEP 5: Pattern Analysis")
    print("-" * 70)
    
    if result.get("patterns"):
        render_patterns(result["patterns"])
        print("✓ Patterns detected and rendered")
    else:
        print("ℹ No patterns detected yet (need more history)")
    
    # Learning summary
    print("STEP 6: Learning Summary")
    print("-" * 70)
    
    summary = get_learning_summary(args.mode)
    if summary:
        print(summary)
        print("✓ Learning summary available")
    
    print("\n" + "="*70)
    print("✓ CLI INTEGRATION TEST PASSED")
    print("="*70 + "\n")
    
    return True


def test_cli_arg_parsing():
    """Test CLI argument parsing."""
    
    print("\n" + "="*70)
    print("CLI UNIT TEST: ARGUMENT PARSING")
    print("="*70 + "\n")
    
    import argparse
    from io import StringIO
    
    # Test valid war mode args
    sys.argv = ["cold.py", "war", "--domain", "career", "--arena", "negotiation"]
    
    try:
        args = parse_args()
        assert args.mode == "war"
        assert args.domain == "career"
        assert args.arena == "negotiation"
        print("✓ War mode args parsed correctly")
    except Exception as e:
        print(f"✗ War mode parsing failed: {e}")
        return False
    
    # Test valid normal mode args
    sys.argv = ["cold.py", "normal", "--domain", "self", "--stakes", "medium"]
    
    try:
        args = parse_args()
        assert args.mode == "normal"
        assert args.domain == "self"
        assert args.stakes == "medium"
        print("✓ Normal mode args parsed correctly")
    except Exception as e:
        print(f"✗ Normal mode parsing failed: {e}")
        return False
    
    # Test validation (missing --arena for war mode)
    class MissingArenaArgs:
        mode = "war"
        domain = "career"
        stakes = "high"
        emotional_load = 0.3
        urgency = 0.3
        fatigue = 0.3
        arena = None
        constraints = []
    
    try:
        validate_args(MissingArenaArgs())
        print("✗ Should have caught missing --arena for war mode")
        return False
    except ValueError:
        print("✓ Correctly caught missing --arena for war mode")
    
    print("\n" + "="*70)
    print("✓ CLI ARGUMENT PARSING TEST PASSED")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        # Test 1: Argument parsing
        if not test_cli_arg_parsing():
            sys.exit(1)
        
        # Test 2: Full CLI flow
        if not test_cli_war_mode_flow():
            sys.exit(1)
        
        print("✓ ALL CLI TESTS PASSED\n")
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
