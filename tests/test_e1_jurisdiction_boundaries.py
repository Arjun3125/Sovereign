"""
E1. MINISTER JURISDICTION BOUNDARIES TEST

Test guarantees:
- Ministers don't evaluate out-of-scope questions
- Jurisdiction boundaries are enforced
- Out-of-scope requests are rejected
"""

import pytest
from typing import Optional, Dict, List


class TestE1_JurisdictionBoundaries:
    """E1: Must guarantee ministers stay within jurisdiction"""
    
    @pytest.fixture
    def minister_system(self):
        """Mock minister system with jurisdiction enforcement"""
        class MinisterSystem:
            def __init__(self):
                self.ministers = {}
                self.query_log = []
            
            def register_minister(self, name: str, jurisdiction: List[str]):
                """Register minister with scope"""
                self.ministers[name] = {
                    "name": name,
                    "jurisdiction": set(jurisdiction),
                    "evaluations": []
                }
            
            def evaluate(self, minister_name: str, question: str, domain: str) -> Optional[Dict]:
                """Evaluate question if within jurisdiction"""
                if minister_name not in self.ministers:
                    return {"error": "Minister not found"}
                
                minister = self.ministers[minister_name]
                self.query_log.append({
                    "minister": minister_name,
                    "question": question,
                    "domain": domain
                })
                
                # Check jurisdiction
                if domain not in minister["jurisdiction"]:
                    return {
                        "status": "rejected",
                        "reason": f"Domain '{domain}' outside jurisdiction",
                        "allowed_domains": list(minister["jurisdiction"])
                    }
                
                # Within jurisdiction - evaluate
                result = {
                    "status": "evaluated",
                    "minister": minister_name,
                    "domain": domain,
                    "answer": f"Answer to: {question}"
                }
                
                minister["evaluations"].append(result)
                return result
        
        return MinisterSystem()
    
    def test_within_jurisdiction_accepted(self, minister_system):
        """Question within jurisdiction is accepted"""
        minister_system.register_minister("career_minister", ["career", "negotiation"])
        
        result = minister_system.evaluate(
            "career_minister",
            "Should I take this job?",
            "career"
        )
        
        assert result["status"] == "evaluated"
    
    def test_out_of_scope_rejected(self, minister_system):
        """Question outside jurisdiction is rejected"""
        minister_system.register_minister("career_minister", ["career"])
        
        result = minister_system.evaluate(
            "career_minister",
            "Is this ethical?",
            "ethics"
        )
        
        assert result["status"] == "rejected"
        assert result["reason"] is not None
    
    def test_multiple_jurisdiction_enforcement(self, minister_system):
        """Minister with multiple domains enforces all"""
        minister_system.register_minister(
            "multi_minister",
            ["career", "negotiation", "relationships"]
        )
        
        # In scope
        result_in = minister_system.evaluate(
            "multi_minister",
            "Question",
            "negotiation"
        )
        assert result_in["status"] == "evaluated"
        
        # Out of scope
        result_out = minister_system.evaluate(
            "multi_minister",
            "Question",
            "medical"
        )
        assert result_out["status"] == "rejected"
    
    def test_no_cross_domain_bleed(self, minister_system):
        """One minister's scope doesn't affect another's"""
        minister_system.register_minister("career_min", ["career"])
        minister_system.register_minister("ethics_min", ["ethics"])
        
        # Career minister rejects ethics
        career_result = minister_system.evaluate(
            "career_min",
            "Is it ethical?",
            "ethics"
        )
        assert career_result["status"] == "rejected"
        
        # Ethics minister accepts ethics
        ethics_result = minister_system.evaluate(
            "ethics_min",
            "Is it ethical?",
            "ethics"
        )
        assert ethics_result["status"] == "evaluated"
    
    def test_jurisdiction_list_provided_on_rejection(self, minister_system):
        """Rejection includes allowed domains"""
        minister_system.register_minister(
            "limited_minister",
            ["domain_a", "domain_b"]
        )
        
        result = minister_system.evaluate(
            "limited_minister",
            "Question",
            "domain_c"
        )
        
        assert "allowed_domains" in result
        assert set(result["allowed_domains"]) == {"domain_a", "domain_b"}
    
    def test_empty_jurisdiction_accepts_nothing(self, minister_system):
        """Minister with empty jurisdiction rejects all"""
        minister_system.register_minister("empty_minister", [])
        
        result = minister_system.evaluate(
            "empty_minister",
            "Any question",
            "any_domain"
        )
        
        assert result["status"] == "rejected"
    
    def test_single_jurisdiction_strict(self, minister_system):
        """Minister with single jurisdiction very strict"""
        minister_system.register_minister("specialist", ["career"])
        
        # Accept
        accept = minister_system.evaluate(
            "specialist",
            "Career question",
            "career"
        )
        assert accept["status"] == "evaluated"
        
        # Reject all others
        for domain in ["negotiation", "ethics", "finance"]:
            reject = minister_system.evaluate(
                "specialist",
                "Question",
                domain
            )
            assert reject["status"] == "rejected"
    
    def test_jurisdiction_case_sensitive(self, minister_system):
        """Jurisdiction matching is case-sensitive"""
        minister_system.register_minister("case_min", ["Career"])
        
        # Lowercase rejected
        result_lower = minister_system.evaluate(
            "case_min",
            "Question",
            "career"
        )
        assert result_lower["status"] == "rejected"
        
        # Correct case accepted
        result_correct = minister_system.evaluate(
            "case_min",
            "Question",
            "Career"
        )
        assert result_correct["status"] == "evaluated"
    
    def test_jurisdiction_enforcement_logged(self, minister_system):
        """All jurisdiction checks are logged"""
        minister_system.register_minister("logged_min", ["domain_a"])
        
        # In scope
        minister_system.evaluate("logged_min", "Q1", "domain_a")
        # Out of scope
        minister_system.evaluate("logged_min", "Q2", "domain_b")
        
        # Both should be logged
        assert len(minister_system.query_log) == 2
        assert all(q["minister"] == "logged_min" for q in minister_system.query_log)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
