import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from core.telemetry.store import TelemetryStore
from core.telemetry.models import DecisionEvent, MinisterEvent, RAGTrace, OverrideEvent, OutcomeEvent
from core.telemetry.ids import uid

t = TelemetryStore()
now = datetime.utcnow()

# Decision
dec_id = uid()
dec = DecisionEvent(
    id=dec_id,
    session_id=uid(),
    context_summary="Smoke test debate",
    stakes="high",
    emotional_load=0.2,
    urgency=0.8,
    fatigue=0.1,
    mode="war",
    timestamp=now,
)
t.append("decision_events", dec)

# Minister events
m1 = MinisterEvent(
    id=uid(),
    timestamp=now,
    decision_id=dec_id,
    minister="Power",
    stance="support",
    confidence=0.85,
    key_points=["Apply pressure", "Exploit leverage"],
    rag_refs=["48L_1"]
)

m2 = MinisterEvent(
    id=uid(),
    timestamp=now,
    decision_id=dec_id,
    minister="Psychology",
    stance="conditional",
    confidence=0.6,
    key_points=["Use charm", "Reduce visibility"],
    rag_refs=["AoS_3"]
)

t.append("minister_events", m1)
t.append("minister_events", m2)

# RAG traces
r = RAGTrace(
    id=uid(),
    decision_id=dec_id,
    source_book="48_Laws_of_Power",
    chapter="Law 1",
    principle="Power Consolidation",
    minister_interpretation="Use scarcity to increase perceived value",
    relevance_score=0.92,
)

t.append("rag_traces", r)

# Override
o = OverrideEvent(
    id=uid(),
    decision_id=dec_id,
    override_type="hard",
    confidence_at_time=0.4,
    was_emotional=True,
    notes="Sovereign chose immediate action",
    timestamp=now,
)

t.append("override_events", o)

# Outcome
out = OutcomeEvent(
    id=uid(),
    decision_id=dec_id,
    observed_outcome="Partial success: leverage gained, reputation slightly harmed",
    satisfaction_score=0.6,
    regret_flag=False,
    learning_notes="Consider softer initial probe next time",
    timestamp=now,
)

t.append("outcome_events", out)

print('Telemetry smoke events written to data/telemetry')
