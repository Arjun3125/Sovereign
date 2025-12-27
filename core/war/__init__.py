"""
War Mode (SAFE, ABSTRACT SIMULATION)

Analyze adversarial scenarios:
- Fiction / games
- Negotiations you're part of
- Career competition
- Self-conflict resolution

No real-world harm. Legal/reversible moves only.

API:

from core.war import WarEngine

engine = WarEngine()
verdict = engine.run(
    objective="outperform rival in market X",
    arena="career",
    constraints=["legal", "reversible", "reputation_safe"],
    state={"fatigue": 0.2, "resources": 0.6}
)

Output:
{
  "VERDICT": "PROCEED | CONDITIONAL | ABORT",
  "PRIMARY_MOVE": description,
  "ALTERNATIVES": [alt1, alt2],
  "RISK": score (0-1),
  "OPTIONALITY": preserved | limited,
  "DO_NOT": [constraints],
  "NEXT": first step
}
"""

from .war_engine import WarEngine
from .opponent_model import build_opponent
from .move_generator import generate_moves
from .counter_simulator import simulate_counters
from .damage_envelope import evaluate_damage
from .war_verdict import build_war_verdict
from .war_memory import log_war_event, resolve_war_outcome, log_war_override
from .war_calibration import calibrate_n_from_war_patterns, get_n_war_posture, summarize_war_learning

__all__ = [
    "WarEngine",
    "build_opponent",
    "generate_moves",
    "simulate_counters",
    "evaluate_damage",
    "build_war_verdict",
    "log_war_event",
    "resolve_war_outcome",
    "log_war_override",
    "calibrate_n_from_war_patterns",
    "get_n_war_posture",
    "summarize_war_learning",
    "log_war_event",
    "resolve_war_outcome",
    "log_war_override"
]

