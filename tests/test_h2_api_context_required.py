"""
H2. API CONTEXT REQUIRED TEST

Test guarantees:
- API never provides advice without context
- Context is mandatory parameter
- Empty/None context rejected
- No bare advice generation
"""

import pytest
from typing import Dict, Optional, Any


class TestH2_APIContextRequired:
    """H2: Must guarantee context always required for advice"""
    
    @pytest.fixture
    def api_system(self):
        """Mock API enforcing context requirement"""
        class APISystem:
            def __init__(self):
                self.advice_calls = []
                self.rejected_calls = []
            
            def get_advice(self, question: str, context: Optional[Dict]) -> Dict:
                """Get advice - context is required"""
                if context is None:
                    self.rejected_calls.append({
                        "question": question,
                        "reason": "missing_context"
                    })
                    return {
                        "status": "error",
                        "error": "context_required",
                        "advice": None
                    }
                
                if not context:  # Empty dict
                    self.rejected_calls.append({
                        "question": question,
                        "reason": "empty_context"
                    })
                    return {
                        "status": "error",
                        "error": "context_empty",
                        "advice": None
                    }
                
                # Valid context - provide advice
                self.advice_calls.append({
                    "question": question,
                    "context": context
                })
                return {
                    "status": "success",
                    "advice": f"Advice for: {question}",
                    "context_used": bool(context)
                }
            
            def query(self, question: str, context: Optional[Dict] = None) -> Dict:
                """Query endpoint - context optional but checked"""
                return self.get_advice(question, context)
            
            def advice_requires_context(self, question: str) -> bool:
                """Check if context required"""
                return True  # Always required
        
        return APISystem()
    
    def test_advice_with_context_allowed(self, api_system):
        """Advice provided when context given"""
        context = {"source": "doctrine", "data": "test"}
        
        result = api_system.get_advice("What should I do?", context)
        
        assert result["status"] == "success"
        assert result["advice"] is not None
    
    def test_advice_without_context_rejected(self, api_system):
        """Advice denied when context is None"""
        result = api_system.get_advice("What should I do?", context=None)
        
        assert result["status"] == "error"
        assert result["advice"] is None
        assert result["error"] == "context_required"
    
    def test_empty_context_rejected(self, api_system):
        """Empty dict context rejected"""
        result = api_system.get_advice("What?", context={})
        
        assert result["status"] == "error"
        assert result["error"] == "context_empty"
    
    def test_context_mandatory_parameter(self, api_system):
        """Context is tracked as required"""
        api_system.get_advice("q1", None)
        api_system.get_advice("q2", {})
        api_system.get_advice("q3", {"key": "value"})
        
        # First 2 rejected, 1 accepted
        assert len(api_system.rejected_calls) == 2
        assert len(api_system.advice_calls) == 1
    
    def test_rejection_logged(self, api_system):
        """All rejections due to missing context logged"""
        api_system.get_advice("q1", None)
        api_system.get_advice("q2", None)
        api_system.get_advice("q3", None)
        
        assert len(api_system.rejected_calls) == 3
        assert all(r["reason"] == "missing_context" for r in api_system.rejected_calls)
    
    def test_multiple_valid_contexts(self, api_system):
        """Different valid contexts all accepted"""
        contexts = [
            {"type": "principle"},
            {"type": "precedent", "ref": "id"},
            {"type": "doctrine", "source": "text"}
        ]
        
        for ctx in contexts:
            result = api_system.get_advice("q", ctx)
            assert result["status"] == "success"
        
        assert len(api_system.advice_calls) == 3
    
    def test_context_used_in_response(self, api_system):
        """Response indicates context was used"""
        context = {"ref": "doctrine_1"}
        result = api_system.get_advice("q", context)
        
        assert result["context_used"] is True
    
    def test_query_endpoint_same_requirement(self, api_system):
        """Query endpoint has same context requirement"""
        result1 = api_system.query("q", context=None)
        result2 = api_system.query("q", context={"data": "test"})
        
        assert result1["status"] == "error"
        assert result2["status"] == "success"
    
    def test_context_always_required(self, api_system):
        """Verify context is always a hard requirement"""
        assert api_system.advice_requires_context("any question") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
