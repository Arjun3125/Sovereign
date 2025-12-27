import sys
sys.path.insert(0,'.')
from core.orchestrator.quick_verdict import QuickEngine

class FakeState:
    stakes='low'
    emotional_load=0.3
    urgency=0.2
    fatigue=0.1

class FakeContext:
    domain='self'
    raw_text='Friends at Parth place, should I go?'
    reversibility='reversible'

qe = QuickEngine()
v = qe.run(FakeContext(), FakeState())
print(v)
print('\n--- Quick Mode test completed ---')
