#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SOVEREIGN MASTER TEST RUNNER (L1 + L2 + L3 + L4 + L5)

Runs all 5 test layers sequentially with gate enforcement.
- Layer 1: Pure Functional Tests (27 tests)
- Layer 2: Memory & Authority Tests (10 tests)
- Layer 3: Debate & Power Tests (9 tests)
- Layer 4: Mode Logic Tests (8 tests)
- Layer 5: E2E Integration Tests (12 tests)

GATE LOGIC: Each layer must pass 100% before next layer proceeds.

Run: python tests/run_all_layers.py
"""

import subprocess
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def run_layer_suite(layer_num: int, layer_name: str, test_files: list) -> tuple[bool, int]:
    """
    Run all tests in a layer and report results.
    Returns: (all_passed: bool, total_tests: int)
    """
    print(f"\n{'=' * 70}")
    print(f"LAYER {layer_num}: {layer_name}")
    print(f"{'=' * 70}")
    
    layer_results = {}
    total_tests = 0
    
    for test_file, suite_name in test_files:
        print(f"\nRunning: {test_file}")
        print("-" * 70)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=line"],
            capture_output=True,
            text=True
        )
        
        # Count tests from output
        passed = result.stdout.count(" PASSED")
        total_tests += passed
        
        passed = result.returncode == 0
        layer_results[suite_name] = passed
        
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {suite_name}: {passed}")
    
    all_passed = all(layer_results.values())
    return all_passed, total_tests


def main():
    print("=" * 70)
    print("SOVEREIGN MASTER TEST RUNNER (L1 + L2)")
    print("=" * 70)
    
    # Layer 1: Pure Functional Tests
    l1_suites = [
        ("tests/unit/test_similarity.py", "Similarity"),
        ("tests/unit/test_retriever.py", "Retriever"),
        ("tests/unit/test_validator.py", "Validator"),
        ("tests/unit/test_indexing.py", "Indexing"),
    ]
    
    l1_passed, l1_count = run_layer_suite(1, "PURE FUNCTIONAL TESTS", l1_suites)
    
    # Gate enforcement: only proceed to L2 if L1 100%
    if not l1_passed:
        print("\n" + "=" * 70)
        print("❌ L1 FAILED — STOPPING HERE")
        print("Fix L1 tests before proceeding to L2")
        print("=" * 70)
        return 1
    
    # Layer 2: Memory & Authority Tests
    l2_suites = [
        ("tests/memory/test_memory_authority.py", "Memory Authority"),
    ]
    
    l2_passed, l2_count = run_layer_suite(2, "MEMORY & AUTHORITY TESTS", l2_suites)
    
    if not l2_passed:
        print("\n" + "=" * 70)
        print("❌ L2 FAILED — STOPPING HERE")
        print("=" * 70)
        return 1
    
    # Layer 3: Debate & Power Dynamics Tests
    l3_suites = [
        ("tests/debate/test_minister_isolation.py", "Minister Isolation"),
    ]
    
    l3_passed, l3_count = run_layer_suite(3, "DEBATE & POWER DYNAMICS TESTS", l3_suites)
    
    if not l3_passed:
        print("\n" + "=" * 70)
        print("❌ L3 FAILED — STOPPING HERE")
        print("=" * 70)
        return 1
    
    # Layer 4: Mode Logic & War Mode Tests
    l4_suites = [
        ("tests/modes/test_war_mode.py", "War Mode"),
    ]
    
    l4_passed, l4_count = run_layer_suite(4, "MODE LOGIC & WAR MODE TESTS", l4_suites)
    
    if not l4_passed:
        print("\n" + "=" * 70)
        print("❌ L4 FAILED — STOPPING HERE")
        print("=" * 70)
        return 1
    
    # Layer 5: End-to-End Integration Tests
    l5_suites = [
        ("tests/e2e/test_integration.py", "E2E Integration"),
    ]
    
    l5_passed, l5_count = run_layer_suite(5, "END-TO-END INTEGRATION TESTS", l5_suites)
    
    print("\n" + "=" * 70)
    print("MASTER TEST SUMMARY (ALL 5 LAYERS)")
    print("=" * 70)
    print("[PASS] L1 (Pure Functional):        " + str(l1_count) + " tests")
    print("[PASS] L2 (Memory & Authority):     " + str(l2_count) + " tests")
    print("[PASS] L3 (Debate & Power):         " + str(l3_count) + " tests")
    print("[PASS] L4 (Mode Logic & War):       " + str(l4_count) + " tests")
    print("[PASS] L5 (End-to-End):             " + str(l5_count) + " tests")
    
    total = l1_count + l2_count + l3_count + l4_count + l5_count
    print("\nTotal: " + str(total) + " tests passing across all 5 layers")
    print("=" * 70)
    
    if all([l1_passed, l2_passed, l3_passed, l4_passed, l5_passed]):
        print("[SUCCESS] ALL 5 LAYERS PASSED - FRAMEWORK COMPLETE")
        print("=" * 70)
        return 0
    else:
        print("[FAILURE] TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
