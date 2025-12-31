#!/usr/bin/env python
"""
SOVEREIGN L2 TEST RUNNER
Memory & Authority Tests

Layer 2: Integration testing for memory store, write authority, doctrine immutability,
and mutation logging. All tests use mock memory store; no external dependencies.

Run: python tests/run_l2.py
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
    print("SOVEREIGN L2 TEST SUITE — MEMORY & AUTHORITY TESTS")
    print("=" * 70)
    
    l2_suites = [
        ("tests/memory/test_memory_authority.py", "Memory Authority & Doctrine Immutability"),
    ]
    
    results = {}
    for test_file, suite_name in l2_suites:
        results[suite_name] = run_test_suite(test_file, suite_name)
    
    print("\n" + "=" * 70)
    print("L2 TEST SUMMARY")
    print("=" * 70)
    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {suite_name}")
    
    all_passed = all(results.values())
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL L2 TESTS PASSED — READY FOR L3")
        print("=" * 70)
        return 0
    else:
        print("❌ L2 TESTS FAILED — DO NOT PROCEED TO L3")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
