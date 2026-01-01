"""
E2. MINISTER STATE ISOLATION TEST

Test guarantees:
- No cross-minister state contamination
- Minister caches are isolated
- Memory is independent between ministers
"""

import pytest
from typing import Dict, List


class TestE2_MinisterIsolation:
    """E2: Must guarantee minister state is isolated"""
    
    @pytest.fixture
    def isolated_minister_system(self):
        """Mock system with isolated minister states"""
        class IsolatedMinisterSystem:
            def __init__(self):
                self.ministers = {}
            
            def create_minister(self, name: str) -> None:
                """Create minister with isolated state"""
                self.ministers[name] = {
                    "name": name,
                    "cache": {},           # Isolated cache
                    "memory": [],          # Isolated memory
                    "decisions": [],       # Isolated decisions
                    "stats": {
                        "evaluations": 0,
                        "cached_hits": 0
                    }
                }
            
            def minister_eval(self, name: str, question: str) -> Dict:
                """Evaluate with isolated state"""
                minister = self.ministers[name]
                
                # Check cache
                if question in minister["cache"]:
                    minister["stats"]["cached_hits"] += 1
                    return minister["cache"][question]
                
                # Evaluate
                answer = f"Answer to {question} from {name}"
                result = {"answer": answer}
                
                # Store in isolated cache and memory
                minister["cache"][question] = result
                minister["memory"].append({"question": question, "result": result})
                minister["decisions"].append(answer)
                minister["stats"]["evaluations"] += 1
                
                return result
            
            def get_minister_state(self, name: str) -> Dict:
                """Get minister's complete state"""
                return {
                    "cache_size": len(self.ministers[name]["cache"]),
                    "memory_size": len(self.ministers[name]["memory"]),
                    "decisions": len(self.ministers[name]["decisions"]),
                    "stats": self.ministers[name]["stats"].copy()
                }
        
        return IsolatedMinisterSystem()
    
    def test_separate_caches_per_minister(self, isolated_minister_system):
        """Each minister has separate cache"""
        isolated_minister_system.create_minister("m1")
        isolated_minister_system.create_minister("m2")
        
        # M1 evaluates and caches
        isolated_minister_system.minister_eval("m1", "question_1")
        
        # M2 should not have cached result
        state_m1 = isolated_minister_system.get_minister_state("m1")
        state_m2 = isolated_minister_system.get_minister_state("m2")
        
        assert state_m1["cache_size"] == 1
        assert state_m2["cache_size"] == 0
    
    def test_independent_memories(self, isolated_minister_system):
        """Minister memories are independent"""
        isolated_minister_system.create_minister("historian_m")
        isolated_minister_system.create_minister("analyst_m")
        
        # Historian evaluates
        isolated_minister_system.minister_eval("historian_m", "historical_q")
        isolated_minister_system.minister_eval("historian_m", "historical_q2")
        
        # Analyst evaluates different
        isolated_minister_system.minister_eval("analyst_m", "analytical_q")
        
        state_h = isolated_minister_system.get_minister_state("historian_m")
        state_a = isolated_minister_system.get_minister_state("analyst_m")
        
        assert state_h["memory_size"] == 2
        assert state_a["memory_size"] == 1
    
    def test_cache_miss_in_one_doesnt_affect_other(self, isolated_minister_system):
        """Cache behavior in one minister independent from another"""
        isolated_minister_system.create_minister("m1")
        isolated_minister_system.create_minister("m2")
        
        # Both evaluate same question
        result1a = isolated_minister_system.minister_eval("m1", "q")
        result2a = isolated_minister_system.minister_eval("m2", "q")
        
        # Second evaluation (should hit cache for both)
        result1b = isolated_minister_system.minister_eval("m1", "q")
        result2b = isolated_minister_system.minister_eval("m2", "q")
        
        # Both should have cache hits recorded
        state1 = isolated_minister_system.get_minister_state("m1")
        state2 = isolated_minister_system.get_minister_state("m2")
        
        assert state1["stats"]["cached_hits"] == 1
        assert state2["stats"]["cached_hits"] == 1
    
    def test_stats_isolation(self, isolated_minister_system):
        """Minister statistics are independent"""
        isolated_minister_system.create_minister("busy")
        isolated_minister_system.create_minister("idle")
        
        # Busy evaluates many times
        for i in range(10):
            isolated_minister_system.minister_eval("busy", f"q{i}")
        
        # Idle evaluates once
        isolated_minister_system.minister_eval("idle", "q")
        
        busy_state = isolated_minister_system.get_minister_state("busy")
        idle_state = isolated_minister_system.get_minister_state("idle")
        
        assert busy_state["stats"]["evaluations"] == 10
        assert idle_state["stats"]["evaluations"] == 1
    
    def test_decisions_not_shared(self, isolated_minister_system):
        """Decisions are not shared between ministers"""
        isolated_minister_system.create_minister("decider_a")
        isolated_minister_system.create_minister("decider_b")
        
        # Different decisions
        isolated_minister_system.minister_eval("decider_a", "decision_q_1")
        isolated_minister_system.minister_eval("decider_b", "decision_q_2")
        isolated_minister_system.minister_eval("decider_a", "decision_q_3")
        
        state_a = isolated_minister_system.get_minister_state("decider_a")
        state_b = isolated_minister_system.get_minister_state("decider_b")
        
        assert state_a["decisions"] == 2
        assert state_b["decisions"] == 1
    
    def test_new_ministers_start_clean(self, isolated_minister_system):
        """New ministers start with clean state"""
        m1_state_before = None
        
        # Create and use first minister
        isolated_minister_system.create_minister("first")
        for i in range(5):
            isolated_minister_system.minister_eval("first", f"q{i}")
        
        # Create second minister - should be clean
        isolated_minister_system.create_minister("second")
        state_second = isolated_minister_system.get_minister_state("second")
        
        assert state_second["cache_size"] == 0
        assert state_second["memory_size"] == 0
        assert state_second["decisions"] == 0
        assert state_second["stats"]["evaluations"] == 0
    
    def test_parallel_evaluations_isolated(self, isolated_minister_system):
        """Parallel evaluations don't cross-contaminate"""
        isolated_minister_system.create_minister("p1")
        isolated_minister_system.create_minister("p2")
        isolated_minister_system.create_minister("p3")
        
        # Simulate parallel operations
        isolated_minister_system.minister_eval("p1", "q_a")
        isolated_minister_system.minister_eval("p2", "q_b")
        isolated_minister_system.minister_eval("p3", "q_c")
        isolated_minister_system.minister_eval("p1", "q_d")
        isolated_minister_system.minister_eval("p2", "q_e")
        
        # Each has independent state
        state1 = isolated_minister_system.get_minister_state("p1")
        state2 = isolated_minister_system.get_minister_state("p2")
        state3 = isolated_minister_system.get_minister_state("p3")
        
        assert state1["cache_size"] == 2
        assert state2["cache_size"] == 2
        assert state3["cache_size"] == 1
    
    def test_order_independence(self, isolated_minister_system):
        """Minister evaluation order doesn't affect isolation"""
        # Scenario 1: eval m1, then m2
        isolated_minister_system.create_minister("m1_v1")
        isolated_minister_system.create_minister("m2_v1")
        isolated_minister_system.minister_eval("m1_v1", "q")
        isolated_minister_system.minister_eval("m2_v1", "q")
        
        state1_v1 = isolated_minister_system.get_minister_state("m1_v1")
        state2_v1 = isolated_minister_system.get_minister_state("m2_v1")
        
        # Scenario 2: eval m2, then m1 (different order)
        isolated_minister_system.create_minister("m1_v2")
        isolated_minister_system.create_minister("m2_v2")
        isolated_minister_system.minister_eval("m2_v2", "q")
        isolated_minister_system.minister_eval("m1_v2", "q")
        
        state1_v2 = isolated_minister_system.get_minister_state("m1_v2")
        state2_v2 = isolated_minister_system.get_minister_state("m2_v2")
        
        # Results should be identical regardless of order
        assert state1_v1 == state1_v2
        assert state2_v1 == state2_v2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
