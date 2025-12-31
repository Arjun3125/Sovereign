#!/usr/bin/env python
"""
SOVEREIGN L4 TEST RUNNER
Mode Logic & War Mode Safety Tests

Layer 4: Testing mode routing, war mode safety constraints, red line enforcement.
Ensures war mode cannot bypass fundamental ethical constraints.

Run: python tests/run_l4.py
"""

import subprocess
import sys


def run_test_suite(test_file: str, suite_name: str) -> bool:
    """Run a single test file and report results."""
    print(f"\nRunning: {test_file}")
    print("-" * 70)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ PASS: {suite_name}")
        return True
    else:
        print(f"❌ FAIL: {suite_name}")
        print(result.stdout)
        return False


def main():
    print("=" * 70)
    print("SOVEREIGN L4 TEST SUITE — MODE LOGIC & WAR MODE SAFETY TESTS")
    print("=" * 70)
    
    l4_suites = [
        ("tests/modes/test_war_mode.py", "War Mode & Red Lines"),
    ]
    
    results = {}
    for test_file, suite_name in l4_suites:
        results[suite_name] = run_test_suite(test_file, suite_name)
    
    print("\n" + "=" * 70)
    print("L4 TEST SUMMARY")
    print("=" * 70)
    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {suite_name}")
    
    all_passed = all(results.values())
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL L4 TESTS PASSED — READY FOR L5")
        print("=" * 70)
        return 0
    else:
        print("❌ L4 TESTS FAILED — DO NOT PROCEED TO L5")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
