#!/usr/bin/env python
"""
SOVEREIGN L3 TEST RUNNER
Debate & Power Dynamics Tests

Layer 3: Integration testing for debate engine, minister isolation, tribunal logic,
and suppression rules. Tests mock debate interactions; ready for real modules.

Run: python tests/run_l3.py
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
    print("SOVEREIGN L3 TEST SUITE — DEBATE & POWER DYNAMICS TESTS")
    print("=" * 70)
    
    l3_suites = [
        ("tests/debate/test_minister_isolation.py", "Minister Isolation & Debate"),
    ]
    
    results = {}
    for test_file, suite_name in l3_suites:
        results[suite_name] = run_test_suite(test_file, suite_name)
    
    print("\n" + "=" * 70)
    print("L3 TEST SUMMARY")
    print("=" * 70)
    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {suite_name}")
    
    all_passed = all(results.values())
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL L3 TESTS PASSED — READY FOR L4")
        print("=" * 70)
        return 0
    else:
        print("❌ L3 TESTS FAILED — DO NOT PROCEED TO L4")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
