"""
Tests for Ministers
Tests for the minister council system.
"""

import unittest
from ministers import GrandStrategist, PowerAnalyst, PsychologyAdvisor


class TestMinisters(unittest.TestCase):
    """Test cases for minister functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategist = GrandStrategist()
        self.power_analyst = PowerAnalyst()
        self.psych_advisor = PsychologyAdvisor()

    def test_minister_initialization(self):
        """Test that ministers initialize correctly."""
        self.assertEqual(self.strategist.name, "Grand Strategist")
        self.assertEqual(self.power_analyst.name, "Power Analyst")

    def test_minister_analysis(self):
        """Test minister analysis methods."""
        context = {"situation": "test"}
        analysis = self.strategist.analyze(context)
        self.assertIsInstance(analysis, dict)
        self.assertIn("minister", analysis)


if __name__ == "__main__":
    unittest.main()
