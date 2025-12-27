"""
N Engine - Decision Synthesis Orchestrator (LOCKED)

N synthesizes debate output into a final verdict.

Flow:
1. Detect illusions (blind spots in human reasoning)
2. Check trajectory (long-term alignment)
3. Weight verdicts (by credibility signals)
4. Decide action posture (abort/force/delay/conditional)
5. Check question gate (is one more question needed?)
6. Build final verdict (if not questioning)

Output: Either { "mode": "question", "question": "..." }
        Or: { "mode": "verdict", "verdict": {...} }

N is the final voice before Sovereign decision.
"""

from typing import Dict, Optional, List, Tuple
from context.context_schema import DecisionContext
from core.debate.debate_schema import MinisterVerdict
from core.n.illusion_detector import IllusionDetector
from core.n.trajectory_check import TrajectoryChecker
from core.n.weighting import MinisterWeighting
from core.n.action_posture import ActionPosture
from core.n.question_gate import QuestionGate
from core.n.verdict import VerdictFormatter


class NEngine:
    """
    N (Synthesis) - Final decision analysis before Sovereign.
    
    Orchestrates all synthesis components:
    - Illusion detection
    - Trajectory assessment
    - Minister weighting
    - Action posture decision
    - Question gate
    - Verdict formatting
    
    Returns either a clarifying question or a final verdict.
    """
    
    def __init__(self):
        """Initialize N engine components."""
        self.illusion_detector = IllusionDetector()
        self.trajectory_checker = TrajectoryChecker()
        self.minister_weighting = MinisterWeighting()
        self.action_posture = ActionPosture()
        self.question_gate = QuestionGate()
        self.verdict_formatter = VerdictFormatter()
    
    def synthesize(
        self,
        debate_output: Dict,
        ctx: DecisionContext
    ) -> Dict:
        """
        Synthesize debate output into verdict or clarifying question.
        
        Args:
            debate_output: Output from DebateEngine
            ctx: Original decision context
            
        Returns:
            { "mode": "question", "question": "..." }
            or
            { "mode": "verdict", "verdict": {...} }
        """
        # Phase 1: Detect illusions
        illusions = self.illusion_detector.detect_illusions(ctx)
        illusion_summary = self.illusion_detector.illusion_summary(illusions)
        
        # Phase 2: Check trajectory
        trajectory = self.trajectory_checker.check_trajectory(ctx)
        trajectory_explanation = self.trajectory_checker.trajectory_explanation(
            trajectory, ctx
        )
        
        # Phase 3: Weight verdicts
        verdicts = [
            MinisterVerdict(
                minister_name=v["minister"],
                position=v["position"],
                warning=v["warning"],
                confidence=v["confidence"],
                evidence=v.get("evidence", []),
                conditions=v.get("conditions", [])
            )
            for v in debate_output.get("verdicts", [])
        ]
        
        weighted_verdicts = self.minister_weighting.weight_verdicts(
            verdicts,
            debate_output.get("objections", []),
            debate_output.get("concessions", [])
        )
        
        # Phase 4: Decide action posture
        top_weight = weighted_verdicts[0]["weight"] if weighted_verdicts else 0
        posture = self.action_posture.decide_posture(
            weighted_verdicts,
            ctx,
            trajectory
        )
        
        posture_rationale = self.action_posture.posture_rationale(
            posture,
            trajectory,
            ctx,
            top_weight
        )
        
        # Phase 5: Check question gate
        if self.question_gate.needs_question(weighted_verdicts, ctx, illusions):
            question = self.question_gate.build_question(
                weighted_verdicts,
                ctx,
                illusions
            )
            
            return {
                "mode": "question",
                "question": question,
                "context": {
                    "illusions": illusions,
                    "trajectory": trajectory,
                    "top_confidence": top_weight
                }
            }
        
        # Phase 6: Build final verdict
        if not weighted_verdicts:
            # No verdicts from debate = abort
            return {
                "mode": "verdict",
                "verdict": {
                    "VERDICT": "ABORT: Insufficient analysis from ministers",
                    "DO_NOT": "Do not proceed without clear minister consensus",
                    "WHY": "Debate produced no viable positions",
                    "COST": "Abort current decision; gather more context",
                    "POSTURE": {
                        "stance": "abort",
                        "rationale": "No minister consensus on viability"
                    },
                    "ILLUSION": {
                        "detected": len(illusions) > 0,
                        "types": illusions,
                        "summary": illusion_summary
                    },
                    "TRAJECTORY": {
                        "assessment": trajectory,
                        "explanation": trajectory_explanation
                    },
                    "CONDITIONS": [],
                    "EVIDENCE": [],
                    "CONFIDENCE": 0.0
                }
            }
        
        top_verdict_dict = weighted_verdicts[0]
        
        final_verdict = self.verdict_formatter.build_verdict(
            posture=posture,
            top_verdict=top_verdict_dict,
            illusions=illusions,
            trajectory=trajectory,
            illusion_summary=illusion_summary,
            trajectory_explanation=trajectory_explanation,
            posture_rationale=posture_rationale
        )
        
        return {
            "mode": "verdict",
            "verdict": final_verdict
        }
    
    def format_for_display(self, synthesis_output: Dict) -> str:
        """
        Format N output for human display.
        
        Args:
            synthesis_output: Output from synthesize()
            
        Returns:
            Formatted string for display
        """
        if synthesis_output["mode"] == "question":
            question = synthesis_output["question"]
            context = synthesis_output.get("context", {})
            
            lines = []
            lines.append("=" * 60)
            lines.append("CLARIFYING QUESTION NEEDED")
            lines.append("=" * 60)
            lines.append(f"\n{question}\n")
            
            if context.get("illusions"):
                lines.append(f"Blind spot detected: {context['illusions']}\n")
            
            lines.append("=" * 60)
            return "\n".join(lines)
        
        else:  # mode == "verdict"
            verdict = synthesis_output["verdict"]
            return self.verdict_formatter.format_for_display(verdict)
