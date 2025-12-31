#!/usr/bin/env python
"""
SOVEREIGN L5 TEST RUNNER
End-to-End Integration Tests

Layer 5: Full system integration testing. Override flow, war escalation,
suppressed synthesis, determinism, memory persistence, error recovery.

Run: python tests/run_l5.py
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
    print("SOVEREIGN L5 TEST SUITE — END-TO-END INTEGRATION TESTS")
    print("=" * 70)
    
    l5_suites = [
        ("tests/e2e/test_integration.py", "E2E Integration"),
    ]
    
    results = {}
    for test_file, suite_name in l5_suites:
        results[suite_name] = run_test_suite(test_file, suite_name)
    
    print("\n" + "=" * 70)
    print("L5 TEST SUMMARY")
    print("=" * 70)
    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {suite_name}")
    
    all_passed = all(results.values())
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL L5 TESTS PASSED — FRAMEWORK COMPLETE")
        print("=" * 70)
        return 0
    else:
        print("❌ L5 TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
