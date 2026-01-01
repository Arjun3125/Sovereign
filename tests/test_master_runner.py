"""
MASTER TEST RUNNER

Orchestrates all 86+ tests across 10 layers (A-J).
Verifies complete system correctness across all dimensions.

Test Inventory:
- Layer A: Doctrine Ingestion (12 tests) ✓
- Layer B: Embedding & Indexing (8 tests) ✓
- Layer C: Doctrine Assembly (10 tests) ✓
- Layer D: Query/Retrieval (8 tests) ✓
- Layer E: Minister System (14 tests) ✓
- Layer F: Tribunal & Escalation (6 tests) ✓
- Layer G: LLM Guards (6 tests) ✓
- Layer H: CLI/API (8 tests) ✓
- Layer I: Failure Modes (8 tests) ✓
- Layer J: Invariants (6 tests) ✓
TOTAL: 86 tests
"""

import pytest
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class MasterTestRunner:
    """Runs all system tests in correct order and generates reports"""
    
    TEST_LAYERS = [
        ("A", "test_ingestion_master.py", "Doctrine Ingestion System", 12),
        ("B", "test_embedding_master.py", "Embedding & Indexing", 8),
        ("C", "test_assembly_master.py", "Doctrine Assembly & Compression", 10),
        ("D", "test_query_master.py", "Query / Retrieval Layer", 8),
        ("E", "test_ministers_master.py", "Minister System", 14),
        ("F", "test_tribunal_master.py", "Tribunal & Escalation Logic", 6),
        ("G", "test_llm_guards_master.py", "Determinism & Safety Guards", 6),
        ("H", "test_cli_api_master.py", "CLI / API Contracts", 8),
        ("I", "test_failure_modes_master.py", "Failure Modes & Corruption Defense", 8),
        ("J", "test_invariants_master.py", "Regression & Constitutional Invariants", 6),
    ]
    
    # Dependencies: if layer X depends on layer Y, list Y first
    LAYER_DEPENDENCIES = {
        "B": ["A"],  # Embedding needs ingestion
        "C": ["A", "B"],  # Assembly needs ingest + embedding
        "D": ["C"],  # Query needs assembly
        "E": ["D"],  # Ministers need query capability
        "F": ["E"],  # Tribunal needs ministers
        "G": ["F"],  # Guards verify output of tribunal
        "H": ["B", "G"],  # CLI needs embedding + guards
        "I": ["A", "B", "C"],  # Failure modes test ingest/embedding/assembly
        "J": [],  # Invariants are fundamental, no dependencies
    }
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.test_root = Path(__file__).parent
    
    def run_all_tests(self, verbose: bool = True) -> bool:
        """Run all tests in dependency order"""
        print("\n" + "="*80)
        print("MASTER TEST RUNNER - COMPLETE SYSTEM VERIFICATION")
        print("="*80 + "\n")
        
        all_passed = True
        layer_order = self._compute_execution_order()
        
        for layer in layer_order:
            layer_info = self._get_layer_info(layer)
            if not layer_info:
                continue
            
            print(f"\n{'='*80}")
            print(f"Layer {layer}: {layer_info['name']}")
            print(f"Expected Tests: {layer_info['expected_tests']}")
            print(f"Dependencies: {self.LAYER_DEPENDENCIES.get(layer, []) or 'None'}")
            print(f"{'='*80}\n")
            
            passed = self._run_layer(layer, layer_info['file'])
            self.results[layer] = {
                "passed": passed,
                "name": layer_info['name'],
                "file": layer_info['file']
            }
            
            if not passed:
                all_passed = False
                print(f"\n⚠️  Layer {layer} FAILED - stopping execution")
                break
            else:
                print(f"\n✅ Layer {layer} PASSED")
        
        self._print_summary()
        return all_passed
    
    def _compute_execution_order(self) -> List[str]:
        """Topological sort of layers by dependencies"""
        order = []
        visited = set()
        
        def visit(layer):
            if layer in visited:
                return
            visited.add(layer)
            
            for dep in self.LAYER_DEPENDENCIES.get(layer, []):
                visit(dep)
            
            order.append(layer)
        
        for layer, _, _, _ in self.TEST_LAYERS:
            visit(layer)
        
        return order
    
    def _get_layer_info(self, layer: str) -> Dict:
        """Get information about a test layer"""
        for l, file, name, count in self.TEST_LAYERS:
            if l == layer:
                return {
                    "file": file,
                    "name": name,
                    "expected_tests": count
                }
        return None
    
    def _run_layer(self, layer: str, filename: str) -> bool:
        """Run all tests in a specific layer"""
        test_file = self.test_root / filename
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        # Run pytest on this file
        args = [
            str(test_file),
            "-v",
            "--tb=short",
            "-ra"
        ]
        
        result = pytest.main(args)
        return result == 0
    
    def _print_summary(self):
        """Print test execution summary"""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        total_layers = len(self.results)
        passed_layers = sum(1 for r in self.results.values() if r["passed"])
        
        print(f"Layers Executed: {total_layers}/10")
        print(f"Layers Passed: {passed_layers}/{total_layers}\n")
        
        for layer, _, name, expected_tests in self.TEST_LAYERS:
            if layer in self.results:
                result = self.results[layer]
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"{status} | Layer {layer}: {result['name']} ({expected_tests} tests)")
        
        total_expected = sum(count for _, _, _, count in self.TEST_LAYERS)
        print(f"\nTotal Tests (Expected): {total_expected}")
        print(f"Status: {'✅ ALL TESTS PASSED' if passed_layers == total_layers else '❌ SOME TESTS FAILED'}")
        print("\n" + "="*80 + "\n")


def run_single_layer(layer: str) -> bool:
    """Run tests for a single layer"""
    runner = MasterTestRunner()
    layer_info = runner._get_layer_info(layer)
    
    if not layer_info:
        print(f"Unknown layer: {layer}")
        return False
    
    print(f"\nRunning Layer {layer}: {layer_info['name']}")
    return runner._run_layer(layer, layer_info['file'])


def run_until_failure() -> bool:
    """Run tests in order until one fails"""
    runner = MasterTestRunner()
    return runner.run_all_tests()


def get_layer_dependencies(layer: str) -> List[str]:
    """Get dependencies for a layer"""
    runner = MasterTestRunner()
    return runner.LAYER_DEPENDENCIES.get(layer, [])


def get_test_statistics() -> Dict:
    """Get statistics about test suite"""
    stats = {
        "total_tests": 0,
        "total_layers": 10,
        "tests_by_layer": {},
        "test_files": []
    }
    
    runner = MasterTestRunner()
    for layer, file, name, count in runner.TEST_LAYERS:
        stats["total_tests"] += count
        stats["tests_by_layer"][layer] = {
            "count": count,
            "name": name,
            "file": file,
            "dependencies": runner.LAYER_DEPENDENCIES.get(layer, [])
        }
        stats["test_files"].append(file)
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Test Runner")
    parser.add_argument("--layer", "-l", help="Run specific layer (A-J)")
    parser.add_argument("--stats", "-s", action="store_true", help="Print test statistics")
    parser.add_argument("--until-failure", "-f", action="store_true", help="Stop at first failure")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_test_statistics()
        print("\n" + "="*80)
        print("TEST SUITE STATISTICS")
        print("="*80)
        print(f"\nTotal Tests: {stats['total_tests']}")
        print(f"Total Layers: {stats['total_layers']}\n")
        
        for layer in sorted(stats["tests_by_layer"].keys()):
            layer_stat = stats["tests_by_layer"][layer]
            deps = layer_stat["dependencies"] or ["None"]
            print(f"Layer {layer}: {layer_stat['count']:2d} tests | {layer_stat['name']}")
            print(f"  File: {layer_stat['file']}")
            print(f"  Dependencies: {', '.join(deps)}\n")
    
    elif args.layer:
        success = run_single_layer(args.layer.upper())
        sys.exit(0 if success else 1)
    
    elif args.until_failure or True:
        success = run_until_failure()
        sys.exit(0 if success else 1)
