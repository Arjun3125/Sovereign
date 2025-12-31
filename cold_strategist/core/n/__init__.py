"""
N Layer - Package Init (LOCKED)

Exports N synthesis components.
"""

from core.n.n_engine import NEngine
from core.n.illusion_detector import IllusionDetector
from core.n.trajectory_check import TrajectoryChecker
from core.n.weighting import MinisterWeighting
from core.n.action_posture import ActionPosture
from core.n.question_gate import QuestionGate
from core.n.verdict import VerdictFormatter

__all__ = [
    "NEngine",
    "IllusionDetector",
    "TrajectoryChecker",
    "MinisterWeighting",
    "ActionPosture",
    "QuestionGate",
    "VerdictFormatter",
]
