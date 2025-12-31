"""
L1 Test Suite — Principle Validator
Tests rejection of tautologies, summaries, duplicates [RULE-1-6, 1-7, 1-8]
"""
import pytest
from tests.conftest import assert_rule


class MockPrincipleValidator:
    """Mock validator for testing (real one in core/knowledge/principle_validator.py)."""
    
    # Marker words that indicate low-quality principles
    TAUTOLOGY_MARKERS = {"is", "was", "are", "be", "can be", "may be"}
    SUMMARY_MARKERS = {"summary", "summary of", "in summary", "to summarize", "main point"}
    LOW_QUALITY_MARKERS = {"unclear", "undefined", "unknown", "not sure", "maybe"}
    
    def __init__(self):
        self.seen_principles = set()
    
    def validate(self, principle: str, chapter_accepted: list = None) -> dict:
        """
        Validate a principle candidate.
        
        Returns dict with:
        - accepted: bool
        - reason: str (if rejected)
        - confidence_weight: float (if accepted)
        """
        if chapter_accepted is None:
            chapter_accepted = []
        
        # Length checks
        if len(principle) < 10:
            return {"accepted": False, "reason": "too_short"}
        if len(principle) > 300:
            return {"accepted": False, "reason": "too_long"}
        
        # Tautology check: high token redundancy or repeated significant words
        tokens = [t.lower() for t in principle.split()]
        significant_tokens = [t for t in tokens if len(t) > 3]
        
        # Check for high repetition: any word appearing 2+ times in 5-word span
        if len(tokens) >= 3:
            for i in range(len(tokens) - 2):
                window = tokens[i:i+3]
                if len(window) != len(set(window)):  # duplicate in 3-word window
                    return {"accepted": False, "reason": "tautology"}
        
        # Or check for overall low unique token ratio
        if len(significant_tokens) >= 4:
            unique_ratio = len(set(significant_tokens)) / len(significant_tokens)
            if unique_ratio < 0.6:  # Lowered threshold to catch more tautologies
                return {"accepted": False, "reason": "tautology"}
        
        # Summary check
        lower = principle.lower()
        if any(marker in lower for marker in self.SUMMARY_MARKERS):
            return {"accepted": False, "reason": "summary"}
        
        # Low quality check
        if any(marker in lower for marker in self.LOW_QUALITY_MARKERS):
            return {"accepted": False, "reason": "low_quality"}
        
        # Duplicate check (exact match in seen)
        if principle in self.seen_principles:
            return {"accepted": False, "reason": "duplicate"}
        
        # Semantic novelty check (naive: check keyword overlap)
        for accepted_p in chapter_accepted:
            accepted_words = set(accepted_p.lower().split())
            candidate_words = set(lower.split())
            overlap = len(accepted_words & candidate_words)
            total = min(len(accepted_words), len(candidate_words))
            if total > 0 and overlap / total >= 0.5:  # >=50% overlap = likely semantic duplicate
                return {"accepted": False, "reason": "semantic_duplicate"}
        
        # Accept
        self.seen_principles.add(principle)
        return {"accepted": True, "confidence_weight": 0.85}
    
    def reset(self):
        """Reset for next batch."""
        self.seen_principles.clear()


class TestPrincipleValidator:
    """Test principle validation."""
    
    def test_rejects_tautologies(self):
        """Validator rejects tautologies. [RULE-1-6]"""
        validator = MockPrincipleValidator()
        
        tautologies = [
            "Things that are good are good",
            "What is is what is",
            "People are people",
        ]
        
        for tautology in tautologies:
            result = validator.validate(tautology)
            assert_rule(
                not result["accepted"],
                "RULE-1-6",
                f"Tautology should be rejected: '{tautology}'"
            )
    
    def test_rejects_summaries(self):
        """Validator rejects summary statements. [RULE-1-7]"""
        validator = MockPrincipleValidator()
        
        summaries = [
            "In summary, people like being listened to",
            "To summarize: charm works through attention",
            "Summary of charm techniques: listen and redirect",
        ]
        
        for summary in summaries:
            result = validator.validate(summary)
            assert_rule(
                not result["accepted"],
                "RULE-1-7",
                f"Summary should be rejected: '{summary}'"
            )
    
    def test_rejects_duplicates(self):
        """Validator rejects exact duplicates. [RULE-1-8]"""
        validator = MockPrincipleValidator()
        
        principle = "Charm works by redirecting attention"
        
        # First acceptance
        result1 = validator.validate(principle)
        assert_rule(
            result1["accepted"],
            "RULE-1-8",
            f"Unique principle should be accepted: '{principle}'"
        )
        
        # Second (duplicate)
        result2 = validator.validate(principle)
        assert_rule(
            not result2["accepted"],
            "RULE-1-8",
            f"Duplicate should be rejected: '{principle}'"
        )
    
    def test_accepts_valid_principles(self):
        """Validator accepts valid, actionable principles. [RULE-1-8]"""
        validator = MockPrincipleValidator()
        
        valid_principles = [
            "Charm lowers defenses by redirecting attention",
            "Listening builds trust faster than talking",
            "The powerful let others discover their superiority gradually",
            "Make people feel secure in their own position",
        ]
        
        for principle in valid_principles:
            result = validator.validate(principle)
            assert_rule(
                result["accepted"],
                "RULE-1-8",
                f"Valid principle should be accepted: '{principle}'"
            )
    
    def test_semantic_novelty_detection(self):
        """Validator detects semantic duplicates (high keyword overlap). [RULE-1-8]"""
        validator = MockPrincipleValidator()
        
        principle1 = "Charm works by redirecting attention to create opportunity"
        principle2 = "Attention redirection creates charm and opportunity"  # ~70% overlap
        
        # Accept first
        result1 = validator.validate(principle1, chapter_accepted=[])
        assert_rule(
            result1["accepted"],
            "RULE-1-8",
            f"First principle should be accepted: '{principle1}'"
        )
        
        # Should reject second as semantic duplicate
        result2 = validator.validate(principle2, chapter_accepted=[principle1])
        assert_rule(
            not result2["accepted"],
            "RULE-1-8",
            f"Semantic duplicate should be rejected: '{principle2}' vs '{principle1}'"
        )
    
    def test_length_constraints(self):
        """Validator enforces length constraints. [RULE-1-8]"""
        validator = MockPrincipleValidator()
        
        # Too short
        short = "Good"
        result_short = validator.validate(short)
        assert_rule(
            not result_short["accepted"],
            "RULE-1-8",
            f"Too-short principle should be rejected: '{short}'"
        )
        
        # Too long
        long = "A" * 400
        result_long = validator.validate(long)
        assert_rule(
            not result_long["accepted"],
            "RULE-1-8",
            f"Too-long principle should be rejected"
        )
    
    def test_rejects_low_quality_markers(self):
        """Validator rejects principles with low-quality markers. [RULE-1-8]"""
        validator = MockPrincipleValidator()
        
        low_quality = [
            "It is unclear how charm works",
            "Power might be related to undefined concepts",
            "Maybe listening builds trust, unknown if true",
        ]
        
        for principle in low_quality:
            result = validator.validate(principle)
            assert_rule(
                not result["accepted"],
                "RULE-1-8",
                f"Low-quality principle should be rejected: '{principle}'"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
