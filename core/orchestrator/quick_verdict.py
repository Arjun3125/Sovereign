"""
Quick Verdict Model and Engine

Quick Mode is a fast, memory-informed synthesis with zero debate.

Components:
- QuickMinisterLine: Single compressed statement from a minister
- QuickVerdict: 1-shot N synthesis with action bias
- QuickEngine: Callable wrapper to execute quick analysis
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskFlag(Enum):
    """Risk flags that trigger escalation."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class QuickMinisterLine:
    """Single statement from a minister (no debate)."""
    minister: str
    line: str
    risk_flag: RiskFlag = RiskFlag.NONE
    
    def __repr__(self) -> str:
        flag_str = f" [RISK: {self.risk_flag.value}]" if self.risk_flag != RiskFlag.NONE else ""
        return f"{self.minister}: {self.line}{flag_str}"


@dataclass
class QuickVerdict:
    """
    1-shot N synthesis: action-biased, no moralizing, no debate.
    
    Output format (fixed):
    - DO: [clear action]
    - AVOID: [one ego-driven mistake]
    - WHY: [one grounded sentence]
    - NOTE: [optional pattern match]
    """
    
    # Fixed output fields
    do: str = ""  # Clear, actionable step
    avoid: str = ""  # Ego-driven trap to sidestep
    why: str = ""  # One grounded reason (max 15 words)
    note: Optional[str] = None  # Pattern match if detected
    
    # Metadata
    mode: str = "quick"
    event_id: str = ""
    ministers_consulted: List[str] = field(default_factory=list)
    minister_lines: List[QuickMinisterLine] = field(default_factory=list)
    
    # Risk escalation
    risk_level: RiskFlag = RiskFlag.NONE
    escalated: bool = False  # True if any minister's risk_flag triggered escalation
    
    # Memory signals
    pattern_detected: Optional[str] = None
    pattern_name: Optional[str] = None
    
    def should_escalate(self) -> bool:
        """Check if any risk flag or high emotional state should escalate."""
        # Auto-escalate if any minister raised risk
        for line in self.minister_lines:
            if line.risk_flag in [RiskFlag.MEDIUM, RiskFlag.HIGH]:
                return True
        
        # Auto-escalate if overall risk is high
        return self.risk_level in [RiskFlag.MEDIUM, RiskFlag.HIGH]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "mode": self.mode,
            "event_id": self.event_id,
            "do": self.do,
            "avoid": self.avoid,
            "why": self.why,
            "note": self.note,
            "ministers_consulted": self.ministers_consulted,
            "minister_lines": [
                {"minister": ml.minister, "line": ml.line, "risk_flag": ml.risk_flag.value}
                for ml in self.minister_lines
            ],
            "pattern_detected": self.pattern_detected,
            "pattern_name": self.pattern_name,
            "escalated": self.escalated,
            "risk_level": self.risk_level.value
        }
    
    def __repr__(self) -> str:
        lines = [
            f"=== QUICK VERDICT ({self.mode.upper()}) ===",
            f"Event ID: {self.event_id}",
            "",
            f"DO:\n{self.do}",
            "",
            f"AVOID:\n{self.avoid}",
            "",
            f"WHY:\n{self.why}"
        ]
        
        if self.note:
            lines.append("")
            lines.append(f"NOTE:\n{self.note}")
        
        if self.escalated:
            lines.append("")
            lines.append(f"⚠️  ESCALATED TO NORMAL MODE (risk flag triggered)")
        
        return "\n".join(lines)


class QuickEngine:
    """
    Quick Mode execution engine.
    
    Compressed flow:
    1. Load stored memory and patterns for domain
    2. Psychology: detect bias from emotional_load + patterns
    3. Optionality: assess reversibility and exits
    4. Truth: reality check the situation
    5. N: 1-shot synthesis
    
    No Darbar. No inter-minister debate. One clean resolution.
    """
    
    def __init__(self):
        """Initialize Quick Engine."""
        self.name = "QuickEngine"
    
    def run(
        self,
        context: Any,
        state: Any,
        memory_events: Optional[List[Dict]] = None,
        detected_patterns: Optional[List[Dict]] = None
    ) -> QuickVerdict:
        """
        Execute quick analysis and return 1-shot verdict.
        
        Args:
            context: Context object with domain, raw_text
            state: State object with emotional_load, stakes, etc.
            memory_events: Past events for this domain (optional)
            detected_patterns: Detected patterns (optional)
            
        Returns:
            QuickVerdict with fixed DO/AVOID/WHY format
        """
        import uuid
        
        event_id = str(uuid.uuid4())
        domain = getattr(context, 'domain', 'self')
        raw_text = getattr(context, 'raw_text', '')
        emotional_load = getattr(state, 'emotional_load', 0.3)
        stakes = getattr(state, 'stakes', 'medium')
        
        # Initialize verdict
        verdict = QuickVerdict(event_id=event_id, mode="quick")
        
        # Step 1: Load memory and detect pattern
        pattern_name = None
        pattern_signal = None
        if detected_patterns:
            # Find first matching pattern
            for p in detected_patterns:
                if p.get('domain') == domain:
                    pattern_name = p.get('pattern_name', '')
                    pattern_signal = p.get('pattern_type', '')
                    break
        
        verdict.pattern_detected = pattern_signal
        verdict.pattern_name = pattern_name
        
        # Step 2: Psychology (bias detection) - internal check (not a minister)
        risk_from_emotion = RiskFlag.NONE
        if emotional_load > 0.7:
            risk_from_emotion = RiskFlag.MEDIUM
        elif emotional_load > 0.5:
            risk_from_emotion = RiskFlag.LOW

        # Expose psychology signal on verdict (but do not create a separate minister)
        if risk_from_emotion != RiskFlag.NONE:
            verdict.risk_level = risk_from_emotion

        # Step 3: Truth (reality check) - always present
        truth_line = "Separate what you fear from what is actually true."
        risk_from_truth = RiskFlag.NONE
        if pattern_name:
            truth_line = f"This resembles {pattern_name} from memory. Are the actual facts the same?"
            risk_from_truth = RiskFlag.LOW

        verdict.minister_lines.append(
            QuickMinisterLine("Truth", truth_line, risk_from_truth)
        )
        verdict.ministers_consulted.append("Truth")

        # Step 4: Optionality (reversibility + exits)
        optionality_line = "You can undo or adjust this later. That's a safety net."
        risk_from_reversibility = RiskFlag.NONE
        reversibility = getattr(context, 'reversibility', 'reversible')
        if reversibility == 'irreversible':
            optionality_line = "This choice is largely irreversible. Verify before acting."
            risk_from_reversibility = RiskFlag.MEDIUM

        verdict.minister_lines.append(
            QuickMinisterLine("Optionality", optionality_line, risk_from_reversibility)
        )
        verdict.ministers_consulted.append("Optionality")

        # Step 5: Domain-specific minister (always present as third minister)
        domain_minister = self._get_domain_minister(domain)
        domain_line = ""
        if domain_minister:
            domain_line = self._generate_domain_line(domain, raw_text)
        else:
            domain_minister = "Domain"
            domain_line = f"In {domain}, consider reversibility and real consequences."

        verdict.minister_lines.append(
            QuickMinisterLine(domain_minister, domain_line, RiskFlag.NONE)
        )
        verdict.ministers_consulted.append(domain_minister)
        
        # Step 6: Synthesize N's 1-shot advice
        self._synthesize_verdict(verdict, domain, emotional_load, pattern_name)
        
        # Check for escalation
        if verdict.should_escalate():
            verdict.escalated = True
            verdict.risk_level = RiskFlag.HIGH

        # Persist a minimal MemoryEvent (best-effort). Quick Mode MUST log.
        try:
            from core.memory.memory_store import MemoryStore
            from core.memory.event_log import MemoryEvent

            # Map emotional load to low/medium/high strings
            if emotional_load <= 0.33:
                emo = "low"
            elif emotional_load <= 0.66:
                emo = "medium"
            else:
                emo = "high"

            me = MemoryEvent(
                event_id=event_id,
                domain=domain,
                stakes=stakes,
                emotional_load=emo,
                ministers_called=verdict.ministers_consulted,
                verdict_position=(verdict.do or ""),
                verdict_posture=("action"),
                illusions_detected=[],
                contradictions_found=0
            )

            store = MemoryStore()
            store.save_event(me)
        except Exception:
            # Swallow errors to avoid breaking Quick Mode flow; logging is best-effort
            pass

        return verdict
    
    def _get_domain_minister(self, domain: str) -> Optional[str]:
        """
        Get domain-specific minister name.
        
        Args:
            domain: Decision domain
            
        Returns:
            Minister name or None
        """
        domain_ministers = {
            'self': 'Personal',
            'career': 'Strategy',
            'relationship': 'Relationship',
            'negotiation': 'Diplomat',
            'conflict': 'Strategist',
            'financial': 'Risk',
            'fictional': 'Narrator'
        }
        
        return domain_ministers.get(domain)
    
    def _generate_domain_line(self, domain: str, situation: str) -> str:
        """
        Generate a domain-specific line (simple heuristic).
        
        Args:
            domain: Decision domain
            situation: User's description
            
        Returns:
            Domain-specific counsel
        """
        if domain == 'career':
            return "Career moves are reversible. Focus on optionality."
        elif domain == 'relationship':
            return "Relationships depend on presence. Showing up matters."
        elif domain == 'negotiation':
            return "In negotiation, silence and patience are strength."
        elif domain == 'conflict':
            return "Conflicts escalate when pride takes the wheel."
        elif domain == 'financial':
            return "Money decisions are reversible if you preserve cash."
        else:
            return f"In {domain}, reality beats narrative."
    
    def _synthesize_verdict(
        self,
        verdict: QuickVerdict,
        domain: str,
        emotional_load: float,
        pattern_name: Optional[str]
    ) -> None:
        """
        Synthesize N's 1-shot action-biased verdict.
        
        Args:
            verdict: QuickVerdict object to fill (in-place)
            domain: Decision domain
            emotional_load: Emotional load level
            pattern_name: Detected pattern, if any
        """
        # Simplified synthesis based on domain and emotion
        
        if domain == 'self':
            if emotional_load > 0.6:
                verdict.do = "Do nothing today. Revisit in 24 hours."
                verdict.avoid = "Acting on a wave of emotion."
                verdict.why = "Reactive decisions usually demand cleanup later."
            else:
                verdict.do = "State your boundary clearly and once."
                verdict.avoid = "Explaining or justifying yourself repeatedly."
                verdict.why = "Clarity beats lengthy justification every time."
        
        elif domain == 'career':
            verdict.do = "Request a private conversation to clarify expectations."
            verdict.avoid = "Escalating before one-on-one dialogue."
            verdict.why = "Most career friction dissolves in direct conversation."
        
        elif domain == 'relationship':
            if pattern_name and 'avoidance' in pattern_name.lower():
                verdict.do = "Show up, stay briefly, leave on your terms."
                verdict.avoid = "Using absence as a pride statement."
                verdict.why = "Your presence costs nothing; absence proves their importance."
            else:
                verdict.do = "Initiate contact without expectation of a specific outcome."
                verdict.avoid = "Letting resentment dictate whether you reach out."
                verdict.why = "Relationships survive on consistent, simple presence."
        
        elif domain == 'negotiation':
            verdict.do = "Make your best offer, then listen."
            verdict.avoid = "Negotiating against yourself or over-explaining."
            verdict.why = "Silence forces the other party to move next."
        
        elif domain == 'conflict':
            verdict.do = "State your position once, then disengage."
            verdict.avoid = "Defending your position repeatedly."
            verdict.why = "Repeated defense looks like weakness masquerading as strength."
        
        else:
            verdict.do = "Move toward the option that preserves reversibility."
            verdict.avoid = "Treating this as a one-shot, irreversible decision."
            verdict.why = "Most decisions are less final than they feel."
        
        # Add pattern note if detected
        if pattern_name:
            verdict.note = f"This is the same pattern as {pattern_name}. The advice that worked then applies now."
