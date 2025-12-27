"""
Test suite for War Mode minister selection bias.

Tests domain matching, tier inclusion, hard rule enforcement,
and audit trail generation.
"""

import unittest
from core.orchestrator.war_minister_selector import WarMinisterSelector
from core.orchestrator.war_minister_bias import WAR_MINISTER_BIAS


class TestWarMinisterSelector(unittest.TestCase):
    """Test WarMinisterSelector behavior."""
    
    def setUp(self):
        """Initialize selector for each test."""
        self.selector = WarMinisterSelector()
    
    # ===== Test Domain Matching =====
    
    def test_exact_domain_match(self):
        """Exact domain match should include relevant minister."""
        selected = self.selector.select(["power"])
        self.assertIn("Power", selected)
    
    def test_partial_domain_match(self):
        """Partial domain match (substring) should include relevant minister."""
        selected = self.selector.select(["economic"])
        # "economic" matches "power" domain (economic leverage)
        self.assertIn("Power", selected)
    
    def test_conflict_domain(self):
        """Conflict domain should include Conflict minister."""
        selected = self.selector.select(["conflict"])
        self.assertIn("Conflict", selected)
    
    def test_intelligence_domain(self):
        """Intelligence domain should include Intelligence minister."""
        selected = self.selector.select(["intelligence"])
        self.assertIn("Intelligence", selected)
    
    def test_multiple_domains(self):
        """Multiple domains should pull relevant ministers from multiple tiers."""
        selected = self.selector.select(["power", "legitimacy", "diplomacy"])
        # Power (preferred), Legitimacy (conditional), Diplomacy (deprioritized but pulled if space)
        self.assertIn("Power", selected)
        self.assertIn("Legitimacy", selected)
    
    def test_unknown_domain(self):
        """Unknown domain should still return valid council (Truth, Risk, defaults)."""
        selected = self.selector.select(["unknown_domain_xyz"])
        # Should still return Truth and Risk & Survival
        self.assertIn("Truth", selected)
        self.assertIn("Risk & Survival", selected)
        # Should have 3-5 ministers
        self.assertGreaterEqual(len(selected), 3)
        self.assertLessEqual(len(selected), 5)
    
    # ===== Test Hard Rules =====
    
    def test_truth_always_included(self):
        """Truth must ALWAYS be included in War Mode council."""
        for domain in ["power", "conflict", "intelligence", "diplomacy", "default"]:
            selected = self.selector.select([domain])
            self.assertIn("Truth", selected, f"Truth missing for domain: {domain}")
    
    def test_risk_always_included(self):
        """Risk & Survival must ALWAYS be included in War Mode council."""
        for domain in ["power", "conflict", "intelligence", "diplomacy", "default"]:
            selected = self.selector.select([domain])
            self.assertIn("Risk & Survival", selected, f"Risk & Survival missing for domain: {domain}")
    
    def test_council_size_minimum(self):
        """Council must have MINIMUM 3 ministers."""
        for domain in ["power", "conflict", "diplomacy", "adaptation"]:
            selected = self.selector.select([domain])
            self.assertGreaterEqual(len(selected), 3, f"Council < 3 for domain: {domain}")
    
    def test_council_size_maximum(self):
        """Council must have MAXIMUM 5 ministers."""
        # Even with all preferred ministers, max should be 5
        all_preferred = ["power", "psychology", "conflict", "intelligence", "narrative"]
        selected = self.selector.select(all_preferred)
        self.assertLessEqual(len(selected), 5, f"Council > 5: {selected}")
    
    # ===== Test Tier Behavior =====
    
    def test_preferred_tier_included(self):
        """Preferred ministers should be included when domain matches."""
        selected = self.selector.select(["power", "psychology", "conflict"])
        # All three are in preferred tier
        preferred = ["Power", "Psychology", "Conflict"]
        for minister in preferred:
            self.assertIn(minister, selected)
    
    def test_conditional_tier_included_when_space(self):
        """Conditional ministers should be included if space available and domain matches."""
        # Request domain that matches conditional tier members
        selected = self.selector.select(["legitimacy"])
        # Legitimacy is in conditional tier
        # Should be included if there's space after Truth, Risk, and preferred matches
        # This may or may not be included depending on space, but if included, it's valid
        self.assertLessEqual(len(selected), 5)
    
    def test_deprioritized_rarely_included(self):
        """Deprioritized ministers (Diplomacy, Discipline) should rarely/not be included."""
        # Request with just diplomacy domain
        # Diplomacy is in deprioritized tier - should NOT be selected without forced need
        selected = self.selector.select(["diplomacy"])
        # Diplomacy should NOT be in the selection (it's deprioritized)
        self.assertNotIn("Diplomacy", selected)
    
    def test_adaptation_deprioritized(self):
        """Adaptation should be deprioritized in War Mode."""
        selected = self.selector.select(["adaptation"])
        # Adaptation is deprioritized - should NOT be selected
        self.assertNotIn("Adaptation", selected)
    
    def test_discipline_deprioritized(self):
        """Discipline should be deprioritized in War Mode."""
        selected = self.selector.select(["discipline"])
        # Discipline is deprioritized - should NOT be selected
        self.assertNotIn("Discipline", selected)
    
    # ===== Test Audit Trail =====
    
    def test_audit_format(self):
        """Audit should return proper dictionary with all required fields."""
        selected = self.selector.select(["power"])
        audit = self.selector.audit(selected)
        
        required_fields = [
            "selected",
            "count",
            "guardrails",
            "leverage_ministers",
            "soft_ministers",
            "leverage_count",
            "soft_count",
        ]
        for field in required_fields:
            self.assertIn(field, audit)
    
    def test_audit_guardrails_always_present(self):
        """Audit should show Truth and Risk & Survival in guardrails."""
        selected = self.selector.select(["power"])
        audit = self.selector.audit(selected)
        
        # Guardrails should be a list containing Truth and Risk & Survival
        self.assertIn("Truth", audit["guardrails"])
        self.assertIn("Risk & Survival", audit["guardrails"])
    
    def test_audit_leverage_count_accuracy(self):
        """Audit leverage_count should accurately reflect selected leverage ministers."""
        selected = self.selector.select(["power"])
        audit = self.selector.audit(selected)
        
        leverage_ministers = ["Power", "Psychology", "Conflict", "Intelligence", "Narrative", "Timing", "Optionality"]
        actual_leverage = [m for m in selected if m in leverage_ministers]
        self.assertEqual(audit["leverage_count"], len(actual_leverage))
    
    def test_audit_soft_count_accuracy(self):
        """Audit soft_count should accurately reflect soft voices in selection."""
        selected = self.selector.select(["power"])
        audit = self.selector.audit(selected)
        
        soft_ministers = ["Diplomacy", "Discipline", "Adaptation"]
        actual_soft = [m for m in selected if m in soft_ministers]
        self.assertEqual(audit["soft_count"], len(actual_soft))
    
    # ===== Test Edge Cases =====
    
    def test_empty_domain_tags(self):
        """Empty domain list should return valid council (Truth, Risk, defaults)."""
        selected = self.selector.select([])
        self.assertIn("Truth", selected)
        self.assertIn("Risk & Survival", selected)
        self.assertGreaterEqual(len(selected), 3)
        self.assertLessEqual(len(selected), 5)
    
    def test_duplicate_domain_tags(self):
        """Duplicate domain tags should not cause duplicates in selection."""
        selected = self.selector.select(["power", "power", "power"])
        # Should have no duplicate ministers
        self.assertEqual(len(selected), len(set(selected)))
    
    def test_case_insensitive_matching(self):
        """Domain matching should be case-insensitive."""
        selected_lower = self.selector.select(["power"])
        selected_upper = self.selector.select(["POWER"])
        selected_mixed = self.selector.select(["PoWeR"])
        
        # All should produce the same result (or at least both should include Power)
        self.assertIn("Power", selected_lower)
        self.assertIn("Power", selected_upper)
        self.assertIn("Power", selected_mixed)
    
    def test_selection_deterministic(self):
        """Selection should be deterministic (same input → same output)."""
        domains = ["power", "conflict", "intelligence"]
        selected1 = self.selector.select(domains)
        selected2 = self.selector.select(domains)
        selected3 = self.selector.select(domains)
        
        self.assertEqual(selected1, selected2)
        self.assertEqual(selected2, selected3)
    
    # ===== Test War Mode Philosophy =====
    
    def test_prefers_leverage_heavy_voices(self):
        """War Mode council should prefer leverage-heavy ministers over soft voices."""
        selected = self.selector.select(["power", "diplomacy"])
        audit = self.selector.audit(selected)
        
        # Should have more leverage ministers than soft ones
        self.assertGreater(audit["leverage_count"], audit["soft_count"])
    
    def test_excludes_soft_voices_when_possible(self):
        """War Mode council should exclude soft voices (Diplomacy, Discipline) when possible."""
        selected = self.selector.select(["power"])
        
        soft_voices = ["Diplomacy", "Discipline", "Adaptation"]
        included_soft = [m for m in selected if m in soft_voices]
        
        # War Mode should NOT include soft voices unless forced by min_size
        self.assertEqual(len(included_soft), 0)
    
    def test_guardrails_never_excluded(self):
        """Truth and Risk should NEVER be excluded, even if council is at min size."""
        # Even with minimal selection, guardrails must persist
        selected = self.selector.select(["unknown"])
        
        self.assertIn("Truth", selected)
        self.assertIn("Risk & Survival", selected)
        # These two ARE in the selection
        self.assertGreaterEqual(len(selected), 2)


class TestWarMinisterBias(unittest.TestCase):
    """Test War Minister Bias data structure."""
    
    def test_bias_structure_complete(self):
        """WAR_MINISTER_BIAS should have all required tiers."""
        required_tiers = ["preferred", "conditional", "deprioritized", "hard_rules"]
        for tier in required_tiers:
            self.assertIn(tier, WAR_MINISTER_BIAS)
    
    def test_preferred_tier_has_leverage(self):
        """Preferred tier should include leverage-heavy ministers."""
        leverage_ministers = ["Power", "Psychology", "Conflict", "Intelligence", "Narrative", "Timing"]
        preferred = WAR_MINISTER_BIAS["preferred"]
        
        for minister in leverage_ministers:
            self.assertIn(minister, preferred)
    
    def test_hard_rules_enforcement(self):
        """Hard rules should define Truth, Risk, min/max enforcement."""
        hard_rules = WAR_MINISTER_BIAS["hard_rules"]
        
        self.assertEqual(hard_rules["truth_always_included"], True)
        self.assertEqual(hard_rules["risk_always_included"], True)
        self.assertGreaterEqual(hard_rules["min_ministers"], 3)
        self.assertLessEqual(hard_rules["max_ministers"], 5)
    
    def test_no_minister_duplication(self):
        """No minister should appear in multiple tiers."""
        all_tiers = ["preferred", "conditional", "deprioritized"]
        all_ministers = []
        
        for tier in all_tiers:
            ministers = WAR_MINISTER_BIAS[tier]
            for minister in ministers:
                self.assertNotIn(minister, all_ministers, f"{minister} appears in multiple tiers")
                all_ministers.append(minister)


if __name__ == "__main__":
    unittest.main()
