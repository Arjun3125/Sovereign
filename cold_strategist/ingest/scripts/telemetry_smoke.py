import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.telemetry import new_id, now, DecisionEvent, append

d = DecisionEvent(
	decision_id=new_id(),
	timestamp=now(),
	mode='standard',
	domain='test',
	raw_context='ctx',
	ministers_called=[],
	ministers_silent=[],
	war_mode_active=False,
	session_id=None,
	parent_decision_id=None,
	war_level=None,
	suppressed_constraints=[],
	ethical_filters_disabled=[],
	justification_snapshot=None,
)
append('decision', d)
print('Wrote decision event')
