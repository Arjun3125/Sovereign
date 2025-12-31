"""Dashboard views for Cold Strategist.

These modules provide read-only, authoritative aggregations over the MemoryStore.
Dashboards are views only — they do not modify system state.
"""

from .patterns_dashboard import patterns_overview
from .override_heatmap import override_heatmap
from .war_usage_dashboard import war_usage_summary
from .minister_reliability import minister_reliability_matrix
from .trajectory_drift import trajectory_drift_report
from .rag_influence import rag_influence_for_advice
from .emotional_outcome import emotional_outcome_stats

__all__ = [
    "patterns_overview",
    "override_heatmap",
    "war_usage_summary",
    "minister_reliability_matrix",
    "trajectory_drift_report",
    "rag_influence_for_advice",
    "emotional_outcome_stats",
]
