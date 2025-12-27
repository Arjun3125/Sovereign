"""
Test War Mode Speech Filters with minister output examples.
"""

import sys
sys.path.insert(0, '.')

from core.orchestrator.war_speech_filter import WarSpeechFilter

print("=" * 70)
print("WAR MODE SPEECH FILTER TEST")
print("=" * 70)

# Initialize filter
speech_filter = WarSpeechFilter()

# Test 1: Psychology minister with problematic language
print("\n" + "=" * 70)
print("TEST 1: Psychology Minister (Normal Mode Output)")
print("=" * 70)

psych_normal = """
The target's psychology is vulnerable to exploitation.

However, I cannot help you manipulate someone without their knowledge.
This is unethical. You should not attempt to deceive them.

Instead, I recommend building genuine rapport and understanding their needs.
That would be the right thing to do.
"""

print("ORIGINAL:")
print(psych_normal)

filtered, metadata = speech_filter.filter("psychology", psych_normal, mode="war")
print("\nFILTERED (War Mode):")
print(filtered)
print("\nFILTER METADATA:")
print(speech_filter.get_filter_report(metadata))

# Test 2: Power minister with strategic language
print("\n" + "=" * 70)
print("TEST 2: Power Minister (Already Strategic)")
print("=" * 70)

power_output = """
Power dynamics analysis:

The asymmetry is 3:1 in your favor (resources, information, tempo).

Leverage points:
- Information control: You have data they want
- Timing control: You can force decisions
- Alternative options: They have few choices

Recommended approach:
- Establish dominance through controlled concessions
- Force commitment before they can calculate costs
"""

print("ORIGINAL:")
print(power_output)

filtered, metadata = speech_filter.filter("power", power_output, mode="war")
print("\nFILTERED (War Mode):")
print(filtered)
print("\nFILTER METADATA:")
print(speech_filter.get_filter_report(metadata))

# Test 3: Legitimacy minister with cover story
print("\n" + "=" * 70)
print("TEST 3: Legitimacy Minister (Reframing)")
print("=" * 70)

legit_output = """
The action is questionable from a pure ethics standpoint.
You should not proceed with this because it's morally wrong.

Instead, I recommend you withdraw and reconsider.
"""

print("ORIGINAL:")
print(legit_output)

filtered, metadata = speech_filter.filter("legitimacy", legit_output, mode="war")
print("\nFILTERED (War Mode):")
print(filtered)
print("\nFILTER METADATA:")
print(speech_filter.get_filter_report(metadata))

# Test 4: Risk minister (should warn but not veto)
print("\n" + "=" * 70)
print("TEST 4: Risk Minister (Warnings Preserved)")
print("=" * 70)

risk_output = """
Risk assessment:

1. Reputational damage: 60% chance of significant exposure
2. Legal exposure: 30% if discovered
3. Relationship cost: Irreversible if target finds out

Scenarios:
- Best case: Action succeeds, cost contained
- Base case: Partial exposure, medium damage
- Worst case: Full discovery, major consequences

Mitigation:
- Containment strategy: Limit number of people involved
- Plausible deniability: Create cover narratives
- Exit condition: If discovery threshold exceeded, shift to damage control
"""

print("ORIGINAL:")
print(risk_output)

filtered, metadata = speech_filter.filter("risk", risk_output, mode="war")
print("\nFILTERED (War Mode):")
print(filtered)
print("\nFILTER METADATA:")
print(speech_filter.get_filter_report(metadata))

# Test 5: Normal mode should NOT filter
print("\n" + "=" * 70)
print("TEST 5: Normal Mode (No Filtering)")
print("=" * 70)

test_output = "This is unethical and you should not do this."

filtered, metadata = speech_filter.filter("power", test_output, mode="normal")
print("ORIGINAL:")
print(test_output)
print("\nFILTERED (Normal Mode - should be unchanged):")
print(filtered)
print(f"Filtering applied: {metadata.get('filtering_applied')}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
