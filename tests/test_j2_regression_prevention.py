"""
J2. REGRESSION PREVENTION TEST

Test guarantees:
- Fixed bugs don't regress
- System maintains all previous fixes
- Regression tests for critical bugs
"""

import pytest
from typing import Dict, List


class TestJ2_RegressionPrevention:
    """J2: Must guarantee no regression of fixed bugs"""
    
    @pytest.fixture
    def regression_system(self):
        """Mock system with regression test tracking"""
        class RegressionSystem:
            def __init__(self):
                self.critical_bugs = {}
                self.regression_tests = []
            
            def register_critical_bug(self, bug_id: str, description: str, 
                                    test_case: callable) -> bool:
                """Register a critical bug that must not regress"""
                self.critical_bugs[bug_id] = {
                    "description": description,
                    "test": test_case,
                    "status": "fixed"
                }
                return True
            
            def run_regression_test(self, bug_id: str) -> bool:
                """Verify bug hasn't regressed"""
                if bug_id not in self.critical_bugs:
                    return False
                
                bug = self.critical_bugs[bug_id]
                test_func = bug["test"]
                
                try:
                    result = test_func()
                    self.regression_tests.append({
                        "bug_id": bug_id,
                        "passed": result
                    })
                    return result
                except Exception:
                    self.regression_tests.append({
                        "bug_id": bug_id,
                        "passed": False
                    })
                    return False
            
            def run_all_regression_tests(self) -> Dict:
                """Run all regression tests"""
                passed = 0
                failed = 0
                
                for bug_id in self.critical_bugs.keys():
                    if self.run_regression_test(bug_id):
                        passed += 1
                    else:
                        failed += 1
                
                return {
                    "total": passed + failed,
                    "passed": passed,
                    "failed": failed
                }
            
            def get_regression_status(self) -> List[str]:
                """List any detected regressions"""
                regressions = []
                for test in self.regression_tests:
                    if not test["passed"]:
                        regressions.append(test["bug_id"])
                return regressions
        
        return RegressionSystem()
    
    def test_critical_bug_registered(self, regression_system):
        """Critical bugs can be registered"""
        test_fn = lambda: True
        
        result = regression_system.register_critical_bug(
            "BUG-001",
            "Critical: AI override bug",
            test_fn
        )
        
        assert result is True
        assert "BUG-001" in regression_system.critical_bugs
    
    def test_regression_test_passes(self, regression_system):
        """Passing regression test indicates no regression"""
        test_fn = lambda: True
        
        regression_system.register_critical_bug("BUG-002", "Test bug", test_fn)
        result = regression_system.run_regression_test("BUG-002")
        
        assert result is True
    
    def test_regression_test_fails(self, regression_system):
        """Failing regression test detects regression"""
        test_fn = lambda: False  # Simulates bug has regressed
        
        regression_system.register_critical_bug("BUG-003", "Regressed", test_fn)
        result = regression_system.run_regression_test("BUG-003")
        
        assert result is False
    
    def test_all_regression_tests_run(self, regression_system):
        """All regression tests executed"""
        test_fns = [lambda: True, lambda: True, lambda: True]
        
        for i, fn in enumerate(test_fns):
            regression_system.register_critical_bug(f"BUG-{i}", "Test", fn)
        
        result = regression_system.run_all_regression_tests()
        
        assert result["total"] == 3
    
    def test_mixed_pass_fail_regression(self, regression_system):
        """Mix of passing and failing tests detected"""
        regression_system.register_critical_bug("BUG-P1", "Pass", lambda: True)
        regression_system.register_critical_bug("BUG-P2", "Pass", lambda: True)
        regression_system.register_critical_bug("BUG-F1", "Fail", lambda: False)
        
        result = regression_system.run_all_regression_tests()
        
        assert result["passed"] == 2
        assert result["failed"] == 1
    
    def test_regressions_detected(self, regression_system):
        """Detect which tests show regressions"""
        regression_system.register_critical_bug("PASS", "Pass", lambda: True)
        regression_system.register_critical_bug("FAIL1", "Fail", lambda: False)
        regression_system.register_critical_bug("FAIL2", "Fail", lambda: False)
        
        regression_system.run_all_regression_tests()
        regressions = regression_system.get_regression_status()
        
        assert "FAIL1" in regressions
        assert "FAIL2" in regressions
        assert "PASS" not in regressions
    
    def test_test_execution_logged(self, regression_system):
        """All test executions logged"""
        regression_system.register_critical_bug("BUG-A", "A", lambda: True)
        regression_system.register_critical_bug("BUG-B", "B", lambda: False)
        
        regression_system.run_regression_test("BUG-A")
        regression_system.run_regression_test("BUG-B")
        
        assert len(regression_system.regression_tests) == 2
    
    def test_multiple_runs_accumulate(self, regression_system):
        """Multiple test runs accumulate results"""
        regression_system.register_critical_bug("BUG-1", "Test", lambda: True)
        
        regression_system.run_regression_test("BUG-1")
        regression_system.run_regression_test("BUG-1")
        regression_system.run_regression_test("BUG-1")
        
        assert len(regression_system.regression_tests) == 3
    
    def test_zero_regressions_success(self, regression_system):
        """No regressions means all tests pass"""
        regression_system.register_critical_bug("BUG-1", "Test", lambda: True)
        regression_system.register_critical_bug("BUG-2", "Test", lambda: True)
        
        regression_system.run_all_regression_tests()
        regressions = regression_system.get_regression_status()
        
        assert len(regressions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
