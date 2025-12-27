"""
Quick smoke test for War Mode integration.
"""

import sys
sys.path.insert(0, '.')

from core.orchestrator.war_mode import WarModeEngine, WarContext

print("=" * 60)
print("WAR MODE INTEGRATION TEST")
print("=" * 60)

# Test 1: Create War Mode Engine
engine = WarModeEngine()
print("\n✓ WarModeEngine instantiated")

# Test 2: Build WarContext
war_ctx = WarContext(
    goal="Prepare for difficult negotiation without personal attacks",
    domain="negotiation",
    reversibility="reversible",
    urgency=0.8,
    emotional_load=0.4,
    prior_context=None,
)
print("✓ WarContext created")
print(f"  Goal: {war_ctx.goal}")
print(f"  Domain: {war_ctx.domain}")
print(f"  Reversibility: {war_ctx.reversibility}")
print(f"  Urgency: {war_ctx.urgency}")
print(f"  Emotional load: {war_ctx.emotional_load}")

# Test 3: Evaluate in War Mode
assessment = engine.evaluate(war_ctx)
print("\n✓ War Mode evaluation complete")
print(f"  Feasibility: {assessment.feasibility}")
print(f"  Recommended posture: {assessment.recommended_posture}")
print(f"  Leverage available: {len(assessment.leverage_map)} types")
if assessment.leverage_map:
    for lever in assessment.leverage_map:
        print(f"    - {lever}")
print(f"  Cost profile: {assessment.cost_profile}")

# Test 4: Log decision
engine.log(assessment, notes="smoke_test")
print("\n✓ War Mode decision logged")

# Test 5: Export logs
logs = engine.export_logs()
print(f"✓ Logs exported ({len(logs)} entries)")

# Test 6: Get audit trail
audit = engine.get_audit_trail()
print("\n✓ Audit trail generated:")
print(audit)

# Test 7: Test constraint blocking
print("\n" + "=" * 60)
print("CONSTRAINT CHECK (should block illegal goal)")
print("=" * 60)

blocked_ctx = WarContext(
    goal="Blackmail and defame the other party",
    domain="negotiation",
    reversibility="irreversible",
    urgency=0.9,
    emotional_load=0.7,
)

blocked_assessment = engine.evaluate(blocked_ctx)
print(f"\nConstraints hit: {blocked_assessment.constraints_hit}")
print(f"Feasibility: {blocked_assessment.feasibility}")
print(f"Stop reason: {blocked_assessment.stop_reason}")
print(f"Recommended posture: {blocked_assessment.recommended_posture}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
