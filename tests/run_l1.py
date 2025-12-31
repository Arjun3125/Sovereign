"""
L1 Test Runner & Validation
Runs all Level 1 tests and validates pass/fail status.
"""
import subprocess
import sys
from pathlib import Path


def run_l1_tests():
    """Run all L1 tests and report results."""
    
    l1_tests = [
        "tests/unit/test_similarity.py",
        "tests/unit/test_retriever.py",
        "tests/unit/test_validator.py",
        "tests/unit/test_indexing.py",
    ]
    
    print("=" * 70)
    print("SOVEREIGN L1 TEST SUITE — PURE FUNCTIONAL TESTS")
    print("=" * 70)
    print()
    
    all_passed = True
    results = {}
    
    for test_file in l1_tests:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"⚠️  {test_file} NOT FOUND (skipping)")
            results[test_file] = "SKIP"
            continue
        
        print(f"Running: {test_file}")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ PASS: {test_file}")
                results[test_file] = "PASS"
            else:
                print(f"❌ FAIL: {test_file}")
                print(result.stdout)
                print(result.stderr)
                results[test_file] = "FAIL"
                all_passed = False
        except Exception as e:
            print(f"❌ ERROR: {test_file} — {e}")
            results[test_file] = "ERROR"
            all_passed = False
        
        print()
    
    # Summary
    print("=" * 70)
    print("L1 TEST SUMMARY")
    print("=" * 70)
    
    for test_file, status in results.items():
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{symbol} {test_file}: {status}")
    
    print()
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL L1 TESTS PASSED — READY FOR L2")
        print("=" * 70)
        return 0
    else:
        print("❌ L1 TESTS FAILED — DO NOT PROCEED TO L2")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_l1_tests())
